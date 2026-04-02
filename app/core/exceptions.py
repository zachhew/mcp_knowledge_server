class AppError(Exception):
    """Base application exception."""


class ConfigurationError(AppError):
    """Raised when application configuration is invalid."""


class DatabaseError(AppError):
    """Raised when a database-level failure occurs."""


class CacheError(AppError):
    """Raised when a cache-level failure occurs."""


class NotFoundError(AppError):
    """Raised when an entity was not found."""


class ConflictError(AppError):
    """Raised when entity state conflicts with requested action."""


class ValidationAppError(AppError):
    """Raised when business validation fails."""
