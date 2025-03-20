import asyncio
import logging
import os
from collections import defaultdict
from typing import Any, Callable, Optional, Union

import aiofiles
import aiohttp
import orjson as json
from aiohttp import ClientPayloadError


class StreamClient:
    __slots__ = (
        "url",
        "api_key",
        "max_line_size",
        "retry_config",
        "event_handlers",
        "logger",
        "_running",
        "_session",
        "_buffer",
        "last_event_id",
        "last_event_id_file",
    )

    class_lock = asyncio.Lock()

    def __init__(
        self,
        url: str,
        api_key: str,
        max_line_size: int = 1_048_576 * 2,  # 2MB
        retry_config: Optional[dict[str, Union[int, float]]] = None,
        load_last_events: bool = False,
        last_event_id_file: str = ".dmtapi/last_event_id.txt",
    ):
        """
        Initialize the StreamClient with the given configuration.

        Args:
            url: Stream endpoint URL
            api_key: API key for authentication
            max_line_size: Maximum buffer size in bytes
            retry_config: Connection retry configuration
            load_last_events: Load last event ID from file
            last_event_id_file: File to save last event ID
        """
        self.url = url
        self.api_key = api_key
        self.max_line_size = max_line_size
        self.retry_config = retry_config or {
            "initial_interval": 0.1,  # Start with fast retry
            "max_interval": 30.0,  # Cap at 30 seconds
            "multiplier": 1.5,  # Exponential backoff
            "max_attempts": None,  # Unlimited retries
        }
        self.last_event_id_file = last_event_id_file
        self.last_event_id = (
            self.load_last_event_id(self.last_event_id_file)
            if load_last_events
            else None
        )

        self.event_handlers = defaultdict(list)
        self.logger = logging.getLogger("StreamClient")
        self._running = False
        self._session = None
        self._buffer = bytearray()

        os.makedirs(".dmtapi", exist_ok=True)

    def on(self, event_type: str) -> Callable:
        """Register event handler (decorator)"""

        def decorator(handler: Callable) -> Callable:
            self.event_handlers[event_type].append(handler)
            return handler

        return decorator

    def register_handler(self, event_type: str, handler: Callable) -> None:
        """Programmatically register event handler"""
        self.event_handlers[event_type].append(handler)

    async def _execute_handlers(self, event_type: str, data: Any) -> None:
        """Execute all handlers for an event type concurrently"""
        handlers = self.event_handlers.get(event_type, [])
        if not handlers:
            return

        tasks = [handler(data) for handler in handlers]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _process_message(self, message: bytes) -> None:
        """Process a complete message from the HTTP/2 stream"""
        if not message:
            return

        try:
            message_str = message.decode("utf-8", errors="ignore")
            if "keepalive" in message_str:
                return

            data = json.loads(message_str)
            event_type = data.get("event")
            event_id = data.get("id")

            if event_id:
                self.last_event_id = event_id
                self.logger.debug(f"Received event ID: {self.last_event_id}")

            if event_type and event_type != "heartbeat":
                event_data = data.get("data")
                await self._execute_handlers(event_type, event_data)

        except json.JSONDecodeError as e:
            self.logger.debug(f"Invalid JSON: {message[:100]}... Error: {e}")
        except Exception as e:
            self.logger.error(f"Error processing message: {e}", exc_info=True)

    async def _handle_chunks(self, response: aiohttp.ClientResponse) -> None:
        """Process incoming chunks efficiently for newline-delimited JSON (NDJSON)"""
        newline = ord("\n")

        async for chunk, _ in response.content.iter_chunks():
            if not self._running:
                break

            # Append chunk to buffer
            self._buffer.extend(chunk)

            # Process complete messages (delimited by newlines)
            while True:
                nl_pos = self._buffer.find(newline)
                if nl_pos == -1:
                    break

                # Extract and process message
                message = self._buffer[:nl_pos]
                del self._buffer[: nl_pos + 1]
                await self._process_message(message)

            # Safety check for buffer overflow
            if len(self._buffer) > self.max_line_size:
                self.logger.warning(
                    f"Buffer exceeded max size ({self.max_line_size}), clearing"
                )
                self._buffer.clear()
            elif len(self._buffer) > self.max_line_size * 0.8:
                self.logger.warning(
                    f"Buffer size at {len(self._buffer)} bytes (80% of max size), consider increasing max size"
                )

    async def _connect(self) -> Optional[aiohttp.ClientResponse]:
        """Establish connection to HTTP/2 stream endpoint"""
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=None),
                connector=aiohttp.TCPConnector(
                    limit=0,  # No connection pooling - persistent connection
                    ttl_dns_cache=300,  # Cache DNS results for 5 minutes
                    use_dns_cache=True,
                    enable_cleanup_closed=True,
                    force_close=False,  # Keep connections alive
                    ssl=False,  # Assuming unencrypted local connection
                ),
            )

        # Add Last-Event-ID header if available for resuming the stream
        headers = {
            "USER-API-KEY": self.api_key,
            "Accept": "application/json",
            "Cache-Control": "no-cache",
        }

        if self.last_event_id:
            headers["Last-Event-ID"] = self.last_event_id
            self.logger.info(f"Resuming from event ID: {self.last_event_id}")

        try:
            response = await self._session.get(
                url=self.url,
                headers=headers,
                allow_redirects=False,  # Prevent redirect overhead
                chunked=True,
            )

            if response.status != 200:
                self.logger.warning(f"Connection failed: HTTP {response.status}")
                response.close()
                return None

            # Log HTTP version being used
            version = response.version
            protocol = (
                "HTTP/2"
                if version.major == 2
                else f"HTTP/{version.major}.{version.minor}"
            )
            self.logger.info(f"Connected using {protocol}")

            return response
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            self.logger.debug(f"Connection error: {e}")
            return None

    async def process_events(self) -> None:
        """Process HTTP/2 stream events with automatic reconnection"""
        self._running = True
        self._buffer.clear()
        attempt = 0

        while self._running:
            response = await self._connect()

            if response:
                # Connection successful - reset backoff
                attempt = 0
                try:
                    await self._handle_chunks(response)
                except ClientPayloadError:
                    self.logger.warning("Connection closed by server")
                except Exception as e:
                    self.logger.exception(f"Error processing events: ", exc_info=e)
                finally:
                    response.close()
            else:
                # Connection failed - apply backoff
                attempt += 1
                wait_time = min(
                    self.retry_config["initial_interval"]
                    * (self.retry_config["multiplier"] ** (attempt - 1)),
                    self.retry_config["max_interval"],
                )

                max_attempts = self.retry_config["max_attempts"]
                if max_attempts and attempt >= max_attempts:
                    self.logger.error(
                        f"Max reconnection attempts ({max_attempts}) reached"
                    )
                    break

                self.logger.info(
                    f"Reconnecting in {wait_time:.2f}s (attempt {attempt})"
                )
                await asyncio.sleep(wait_time)

    async def start(self) -> None:
        """Start processing events in background task"""
        self._running = True
        asyncio.create_task(self.process_events())

    async def stop(self) -> None:
        """Stop event processing and cleanup resources"""
        self._running = False
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
        self._buffer.clear()

    async def save_last_event_id(self) -> None:
        """Save last event ID to file for persistence"""
        if self.last_event_id:
            async with self.class_lock:
                try:
                    with aiofiles.open(self.last_event_id_file, "w") as f:
                        await f.write(self.last_event_id)
                    self.logger.info(f"Saved last event ID: {self.last_event_id}")
                except Exception as e:
                    self.logger.error(f"Failed to save event ID: {e}")

    @staticmethod
    def load_last_event_id(last_event_id_file: str) -> Optional[str]:
        """Load last event ID from file. Call once when initializing the client"""
        os.makedirs(".dmtapi", exist_ok=True)

        if not os.path.exists(last_event_id_file) or not os.path.isfile(
            last_event_id_file
        ):
            return None

        try:
            with open(last_event_id_file, "r") as f:
                event_id = f.read().strip()
            return event_id if event_id else None
        except Exception as e:
            logging.error(f"Failed to load event ID: {e}")
            return None
