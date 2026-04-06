"""Package-specific exceptions."""


class IgStrandAlignError(Exception):
    """Base exception for the modular package."""


class MissingTemplateError(IgStrandAlignError):
    """Raised when a requested 2D template cannot be found."""


class DomainNotFoundError(IgStrandAlignError):
    """Raised when a requested domain cannot be resolved."""


class NumberingGenerationError(IgStrandAlignError):
    """Raised when IgStrand numbering cannot be loaded or generated."""
