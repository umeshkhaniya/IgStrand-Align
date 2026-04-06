"""Alignment result models."""

from dataclasses import dataclass, field

from ..core.models import DomainRecord


@dataclass
class Alignment1DResult:
    """Tabular 1D alignment output."""

    domains: list[DomainRecord] = field(default_factory=list)
    ig_labels: list[str] = field(default_factory=list)
    metadata_headers: list[str] = field(
        default_factory=lambda: [
            "structure",
            "refpdbname",
            "tmscore",
            "Igtype",
            "3dD_res_range",
            "igD_res_range",
            "seqid",
            "nresAlign",
            "undefined_info",
        ]
    )


@dataclass
class Alignment2DPanel:
    """A single rendered 2D panel selection."""

    domain: DomainRecord
    template_name: str
    reference_structure: str


@dataclass
class Alignment2DResult:
    """Batch 2D alignment output."""

    panels: list[Alignment2DPanel] = field(default_factory=list)
