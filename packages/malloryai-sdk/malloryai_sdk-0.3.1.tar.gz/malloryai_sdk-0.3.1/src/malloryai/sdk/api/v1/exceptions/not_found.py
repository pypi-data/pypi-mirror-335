from malloryai.sdk.api.v1.exceptions.exception import APIError


class NotFoundError(APIError):
    """Exception for 404 errors."""

    def __init__(self, message: str = "Not Found"):
        super().__init__(404, message)
