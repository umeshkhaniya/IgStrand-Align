"""Application orchestration for the modular IgStrand-Align package."""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from .alignment.alignment_1d import Alignment1DBuilder
from .alignment.alignment_2d import Alignment2DBuilder
from .core.config import AppConfig
from .core.models import OutputArtifact, StructureRequest
from .domain_detection.detector import DomainDetector
from .io.output_writer_1d import OutputWriter1D
from .io.output_writer_2d import OutputWriter2D
from .numbering.service import NumberingService


@dataclass
class IgStrandAlignApp:
    """Coordinates IO, numbering, domain detection, and alignment."""

    config: AppConfig
    numbering_service: NumberingService
    domain_detector: DomainDetector
    alignment_1d_builder: Alignment1DBuilder
    alignment_2d_builder: Alignment2DBuilder
    output_writer_1d: OutputWriter1D
    output_writer_2d: OutputWriter2D

    def resolve_domains(self, requests: Sequence[StructureRequest]):
        """Resolve the requested domains into normalized records."""
        resolved = []
        for request in requests:
            numbering_doc = self.numbering_service.get_structure_numbering(request.pdb_id)
            resolved.append(self.domain_detector.select_domain(numbering_doc, request))
        return resolved

    def build_outputs(
        self,
        requests: Sequence[StructureRequest],
        dimensions: Iterable[str],
    ) -> dict[str, object]:
        """Build the requested alignment outputs from a batch of requests."""
        domains = self.resolve_domains(requests)
        results: dict[str, object] = {}

        if "1D" in dimensions:
            results["1D"] = self.alignment_1d_builder.build(domains)
        if "2D" in dimensions:
            results["2D"] = self.alignment_2d_builder.build(domains)

        return results

    def write_outputs(
        self,
        requests: Sequence[StructureRequest],
        dimensions: Iterable[str],
        input_file_name: str,
    ) -> list[OutputArtifact]:
        """Build and persist outputs for the requested dimensions."""
        dimension_set = {dim.strip() for dim in dimensions if dim.strip()}
        results = self.build_outputs(requests, dimension_set)
        artifacts: list[OutputArtifact] = []
        output_stem = Path(input_file_name).stem

        if "1D" in results:
            destination = (
                self.config.output_dir
                / f"1D_mapping_{output_stem}{self.config.numbering_name.lower()}.xlsx"
            )
            written_path = self.output_writer_1d.write(results["1D"], destination)
            artifacts.append(OutputArtifact(dimension="1D", path=str(written_path)))

        if "2D" in dimension_set:
            destination = (
                self.config.output_dir
                / f"2D_mapping_{output_stem}{self.config.numbering_name.lower()}.xlsx"
            )
            written_path = self.output_writer_2d.write(results["2D"], destination)
            artifacts.append(OutputArtifact(dimension="2D", path=str(written_path)))

        return artifacts
