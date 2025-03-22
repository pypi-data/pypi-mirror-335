from functools import wraps

def requires_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        from ecotrade.authentication import Auth  

        if not Auth._authenticated:
            raise PermissionError("Auth is required before using this function.")
        return func(*args, **kwargs)
    return wrapper
