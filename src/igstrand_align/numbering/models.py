"""Numbering document models."""

from dataclasses import dataclass, field


@dataclass
class RawNumberingDocument:
    """Raw cached or generated numbering payload."""

    pdb_id: str
    numbering_name: str
    content: str
    parsed: list[dict] = field(default_factory=list)
