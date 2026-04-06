"""Cache helpers for numbering documents."""

from .models import RawNumberingDocument


class NumberingCache:
    """Simple in-memory cache for numbering documents."""

    def __init__(self):
        self._items: dict[tuple[str, str], RawNumberingDocument] = {}

    def get(self, pdb_id: str, numbering_name: str):
        return self._items.get((pdb_id.upper(), numbering_name))

    def put(self, document: RawNumberingDocument):
        self._items[(document.pdb_id.upper(), document.numbering_name)] = document
