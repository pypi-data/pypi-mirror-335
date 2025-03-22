class PostRequestError(Exception):
    def __init__(
        self,
        message: str = "POST request error occurred.",
        status_code: int | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code


class GetRequestError(Exception):
    def __init__(
        self,
        message: str = "GET request error occurred.",
        status_code: int | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
