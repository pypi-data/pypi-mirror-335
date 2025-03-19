class LiberalAlphaError(Exception):
    """Base exception for Liberal Alpha SDK errors"""
    pass


class ConnectionError(LiberalAlphaError):
    """Exception raised when the gRPC client fails to connect"""

    def __init__(self, message="Failed to connect to the gRPC server", details=None):
        self.message = message
        self.details = details
        super().__init__(self.__str__())

    def __str__(self):
        error_str = f"ConnectionError: {self.message}"
        if self.details:
            error_str += f" - Details: {self.details}"
        return error_str


class RequestError(LiberalAlphaError):
    """Exception raised when sending a request to the gRPC server fails"""

    def __init__(self, message="Request to gRPC server failed", code=None, details=None):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.__str__())

    def __str__(self):
        error_str = f"RequestError: {self.message}"
        if self.code:
            error_str += f" (code: {self.code})"
        if self.details:
            error_str += f" - Details: {self.details}"
        return error_str
