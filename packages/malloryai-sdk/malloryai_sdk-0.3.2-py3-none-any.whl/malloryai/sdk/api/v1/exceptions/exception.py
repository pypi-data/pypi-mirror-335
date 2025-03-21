class APIError(Exception):
    """Custom exception for API errors."""

    def __init__(self, status_code: int, message: str):
        super().__init__(f"APIError {status_code}: {message}")
        self.status_code = status_code
        self.message = message
