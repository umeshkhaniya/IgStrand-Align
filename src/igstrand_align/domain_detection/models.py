"""Domain detection models."""

from dataclasses import dataclass, field


@dataclass
class DetectedDomain:
    """A domain candidate discovered within a structure."""

    structure_id: str
    chain_id: str
    domain_order: int
    ig_residue_range: str
    metadata: dict[str, object] = field(default_factory=dict)
