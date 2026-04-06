"""Template loading helpers for 2D alignment assets."""

from pathlib import Path
from typing import Union

from ..core.exceptions import MissingTemplateError


class TemplateRepository:
    """Locate template workbooks by Ig type and numbering scheme."""

    def __init__(self, template_dir: Union[str, Path]):
        self.template_dir = Path(template_dir)

    def template_path(self, ig_type: str, numbering_name: str) -> Path:
        return self.template_dir / f"{numbering_name.lower()}_template_{ig_type}.xlsx"

    def resolve_template_path(self, ig_type: str, numbering_name: str) -> Path:
        candidates = [ig_type]
        if ig_type == "IgV_Adash":
            candidates.extend(["IgV_A_Adash", "IgV_A"])

        for candidate in candidates:
            path = self.template_path(candidate, numbering_name)
            if path.is_file():
                return path

        raise MissingTemplateError(
            f"No template file found for {ig_type!r} in {self.template_dir}."
        )
