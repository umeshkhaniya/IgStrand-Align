"""Persistence helpers for cached numbering mapping files."""

from pathlib import Path
from typing import Union


class MappingRepository:
    """Loads and stores cached numbering documents."""

    def __init__(self, mapping_dir: Union[str, Path]):
        self.mapping_dir = Path(mapping_dir)

    def mapping_path(self, pdb_id: str, numbering_name: str) -> Path:
        return self.mapping_dir / f"{pdb_id.upper()}_refnum_{numbering_name}.json"

    def exists(self, pdb_id: str, numbering_name: str) -> bool:
        return self.mapping_path(pdb_id, numbering_name).is_file()

    def load_text(self, pdb_id: str, numbering_name: str) -> str:
        return self.mapping_path(pdb_id, numbering_name).read_text()

    def save_text(self, pdb_id: str, numbering_name: str, contents: str) -> Path:
        path = self.mapping_path(pdb_id, numbering_name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents)
        return path
