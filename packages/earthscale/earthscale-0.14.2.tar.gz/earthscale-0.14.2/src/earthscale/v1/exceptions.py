"""Exceptions for the Earthscale client."""


class EarthscaleClientError(Exception):
    """Base exception for Earthscale client errors."""

    def __init__(self, message: str, error_class: str | None = None):
        self.message = message
        self.error_class = error_class
        super().__init__(message)


class AuthenticationError(EarthscaleClientError):
    """Raised when authentication fails."""

    pass


class NotFoundError(EarthscaleClientError):
    """Raised when a resource is not found."""

    pass


class ValidationFailedError(EarthscaleClientError):
    """Raised when validation fails."""

    pass


class TokenRefreshRequired(EarthscaleClientError):
    """Raised when a token refresh is required."""

    pass


class VersionIncompatibleError(EarthscaleClientError):
    """Raised when the client version is incompatible with the server."""

    pass
