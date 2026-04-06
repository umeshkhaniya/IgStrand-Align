"""CLI entry point scaffold for the modular package."""

import argparse
from pathlib import Path
import sys

from .alignment.alignment_1d import Alignment1DBuilder
from .alignment.alignment_2d import Alignment2DBuilder
from .app import IgStrandAlignApp
from .core.config import AppConfig
from .core.exceptions import IgStrandAlignError
from .domain_detection.detector import DomainDetector
from .io.input_reader import read_structure_requests
from .io.mapping_repository import MappingRepository
from .io.output_writer_1d import OutputWriter1D
from .io.output_writer_2d import OutputWriter2D
from .io.template_repository import TemplateRepository
from .numbering.icn3d_refnum_runner import Icn3dRefnumRunner
from .numbering.parser import NumberingParser
from .numbering.service import NumberingService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate 1D and/or 2D IgStrand alignments."
    )
    parser.add_argument(
        "-f",
        "--file",
        required=True,
        help="Input file containing PDB ID, chain ID, and domain number.",
    )
    parser.add_argument(
        "-d",
        "--dimension",
        required=True,
        choices=["1D", "2D", "1D,2D", "2D,1D"],
        help="Output dimension: 1D, 2D, or 1D,2D.",
    )
    return parser


def build_app() -> IgStrandAlignApp:
    """Construct the modular application with default repositories and services."""
    repo_root = Path(__file__).resolve().parents[2]
    config = AppConfig(
        input_dir=repo_root / "input",
        output_dir=repo_root / "output",
        template_dir=repo_root / "input" / "igstrand_template",
        mapping_dir=repo_root / "input" / "number_mapping_files",
    )
    numbering_service = NumberingService(
        numbering_name=config.numbering_name,
        mapping_repository=MappingRepository(config.mapping_dir),
        parser=NumberingParser(),
        runner=Icn3dRefnumRunner(repo_root / "src" / "refnum.js"),
    )
    return IgStrandAlignApp(
        config=config,
        numbering_service=numbering_service,
        domain_detector=DomainDetector(),
        alignment_1d_builder=Alignment1DBuilder(),
        alignment_2d_builder=Alignment2DBuilder(),
        output_writer_1d=OutputWriter1D(),
        output_writer_2d=OutputWriter2D(
            template_repository=TemplateRepository(config.template_dir),
            numbering_name=config.numbering_name,
            template_dimensions=config.template_dimensions,
        ),
    )


def main() -> int:
    """Run the modular application for the implemented dimensions."""
    parser = build_parser()
    args = parser.parse_args()

    try:
        app = build_app()
        requests = read_structure_requests(args.file)
        artifacts = app.write_outputs(
            requests=requests,
            dimensions=args.dimension.split(","),
            input_file_name=args.file,
        )
    except IgStrandAlignError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    for artifact in artifacts:
        print(f"{artifact.dimension} output written to {artifact.path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
