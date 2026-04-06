"""Shared data models for the modular package."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class StructureRequest:
    """A single requested structure/chain/domain selection."""

    pdb_id: str
    chain_id: str
    domain_index: int


@dataclass(frozen=True)
class ResidueMapping:
    """A residue assignment at a specific IgStrand label."""

    ig_label: str
    residue_code: str
    is_loop: bool = False


@dataclass
class DomainRecord:
    """Normalized domain metadata plus residue numbering assignments."""

    structure_id: str
    ref_pdb_name: str
    ig_type: str
    domain_order: int
    domain_residue_range: str
    ig_residue_range: str
    tm_score: Optional[float] = None
    seq_id: Optional[float] = None
    n_res_aligned: Optional[int] = None
    undefined_residues: list[str] = field(default_factory=list)
    residue_map: dict[str, ResidueMapping] = field(default_factory=dict)


@dataclass(frozen=True)
class OutputArtifact:
    """Information about a generated output file."""

    dimension: str
    path: str
