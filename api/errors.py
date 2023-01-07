class AppError(Exception):
    def __init__(self, message: str = "", status_code=500, *args, **kwargs) -> None:
        super().__init__(message, *args, **kwargs)
        self.status_code = status_code


class InvalidUrl(AppError):
    def __init__(self, url: str):
        super().__init__(
            message=f"URL {url} is invalid" if url else "Please provide a URL",
            status_code=400,
        )


class UrlNotFound(AppError):
    def __init__(self, url: str):
        super().__init__(message=f"URL {url} not found or has expired", status_code=404)


class ExpiredUrl(AppError):
    def __init__(self, url: str):
        super().__init__(message=f"URL {url} has expired", status_code=410)


class ShortUrlTaken(AppError):
    pass
