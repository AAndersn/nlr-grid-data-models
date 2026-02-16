"""Exceptions for gdm_mcp."""


class GDMMCPException(Exception):
    """Base exception for all gdm_mcp errors."""

    pass


class ValidationError(GDMMCPException):
    """Raised when system validation fails."""

    pass


class MergeConflictError(GDMMCPException):
    """Raised when merging systems with conflicts in strict mode."""

    def __init__(self, conflicts: list[dict], message: str = "Merge conflict detected"):
        self.conflicts = conflicts
        super().__init__(message)


class DisaggregationError(GDMMCPException):
    """Raised when system disaggregation fails."""

    pass


class ComponentNotFoundError(GDMMCPException):
    """Raised when a component cannot be found."""

    pass


class InvalidSystemError(GDMMCPException):
    """Raised when a system is invalid or corrupted."""

    pass


class FixApplicationError(GDMMCPException):
    """Raised when applying a fix fails."""

    pass


class TopologyError(GDMMCPException):
    """Raised when topology analysis fails."""

    pass
