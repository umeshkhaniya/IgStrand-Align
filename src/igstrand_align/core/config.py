"""Configuration models for the modular package."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    """Runtime paths and shared application settings."""

    input_dir: Path = Path("../input")
    output_dir: Path = Path("../output")
    numbering_name: str = "igstrand"
    template_dir: Path = Path("../input/igstrand_template")
    mapping_dir: Path = Path("../input/number_mapping_files")
    template_dimensions: dict[str, int] = field(
        default_factory=lambda: {"V_column_range": 21, "V_row_range": 47}
    )
