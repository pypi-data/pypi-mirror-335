import zoneinfo
from datetime import timedelta, datetime
from typing import Generator


def daterange(start_date: datetime, end_date: datetime) -> Generator[datetime]:
    for n in range(int((end_date - start_date).days) + 1):
        yield (start_date + timedelta(n)).astimezone(
            tz=zoneinfo.ZoneInfo("Australia/Brisbane")
        )


def count_daterange(start_date: datetime, end_date: datetime) -> int:
    return int((end_date - start_date).days)
