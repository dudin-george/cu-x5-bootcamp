"""Custom exceptions for the application."""


class BaseAppException(Exception):
    """Base exception for application errors."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        """Initialize exception.

        Args:
            message: Error message.
            status_code: HTTP status code.
        """
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(BaseAppException):
    """Exception raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found") -> None:
        """Initialize exception.

        Args:
            message: Error message.
        """
        super().__init__(message, status_code=404)


class UnauthorizedException(BaseAppException):
    """Exception raised when user is not authorized."""

    def __init__(self, message: str = "Unauthorized") -> None:
        """Initialize exception.

        Args:
            message: Error message.
        """
        super().__init__(message, status_code=401)


class ForbiddenException(BaseAppException):
    """Exception raised when user does not have permission."""

    def __init__(self, message: str = "Forbidden") -> None:
        """Initialize exception.

        Args:
            message: Error message.
        """
        super().__init__(message, status_code=403)


class BadRequestException(BaseAppException):
    """Exception raised when request is invalid."""

    def __init__(self, message: str = "Bad request") -> None:
        """Initialize exception.

        Args:
            message: Error message.
        """
        super().__init__(message, status_code=400)


class ConflictException(BaseAppException):
    """Exception raised when there is a conflict."""

    def __init__(self, message: str = "Conflict") -> None:
        """Initialize exception.

        Args:
            message: Error message.
        """
        super().__init__(message, status_code=409)
