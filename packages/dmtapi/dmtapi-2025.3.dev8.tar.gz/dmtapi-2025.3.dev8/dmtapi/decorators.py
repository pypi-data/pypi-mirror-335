from functools import wraps


def check_provided_access_token(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        access_token = kwargs.get("access_token")
        login = kwargs.get("login")
        server = kwargs.get("server")

        if not access_token and (not login or not server):
            raise ValueError("Access token or login and server must be provided")

        return await func(*args, **kwargs)

    return wrapper
