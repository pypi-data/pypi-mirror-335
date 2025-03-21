from malloryai.sdk.api.v1.exceptions.exception import APIError


class ValidationError(APIError):
    """Exception for 422 validation errors."""

    def __init__(self, message: str = "Validation Error"):
        super().__init__(422, message)
