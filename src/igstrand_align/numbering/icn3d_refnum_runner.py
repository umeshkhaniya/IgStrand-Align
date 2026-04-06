"""Process runner scaffold for generating numbering via the ICN3D Node script."""

from pathlib import Path
import subprocess
from typing import Union

from ..core.exceptions import NumberingGenerationError


class Icn3dRefnumRunner:
    """Run the legacy Node-based numbering generator."""

    def __init__(self, script_path: Union[str, Path]):
        self.script_path = Path(script_path)

    def generate(self, pdb_id: str) -> str:
        result = subprocess.run(
            ["node", str(self.script_path), pdb_id.upper()],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0 or len(result.stdout.strip()) <= 3:
            raise NumberingGenerationError(
                f"Failed to generate numbering for {pdb_id}: {result.stderr.strip()}"
            )
        return result.stdout
