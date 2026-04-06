"""Package-specific exceptions."""


class IgStrandAlignError(Exception):
    """Base exception for the modular package."""


class DependencyError(IgStrandAlignError):
    """Raised when an optional runtime dependency is required but missing."""


class InputFormatError(IgStrandAlignError):
    """Raised when the user-provided input file is missing or malformed."""


class MissingTemplateError(IgStrandAlignError):
    """Raised when a requested 2D template cannot be found."""


class DomainNotFoundError(IgStrandAlignError):
    """Raised when a requested domain cannot be resolved."""


class NumberingGenerationError(IgStrandAlignError):
    """Raised when IgStrand numbering cannot be loaded or generated."""
