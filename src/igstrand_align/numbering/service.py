"""Numbering service orchestration."""

from typing import Optional

from ..core.exceptions import NumberingGenerationError
from .cache import NumberingCache
from .icn3d_refnum_runner import Icn3dRefnumRunner
from .parser import NumberingParser


class NumberingService:
    """Load cached numbering or generate it on demand."""

    def __init__(
        self,
        numbering_name,
        mapping_repository,
        parser: NumberingParser,
        runner: Optional[Icn3dRefnumRunner] = None,
        cache: Optional[NumberingCache] = None,
    ):
        self.numbering_name = numbering_name
        self.mapping_repository = mapping_repository
        self.parser = parser
        self.runner = runner
        self.cache = cache or NumberingCache()

    def get_structure_numbering(self, pdb_id: str):
        cached = self.cache.get(pdb_id, self.numbering_name)
        if cached is not None:
            return cached

        if self.mapping_repository.exists(pdb_id, self.numbering_name):
            contents = self.mapping_repository.load_text(pdb_id, self.numbering_name)
            document = self.parser.parse(pdb_id, self.numbering_name, contents)
            self.cache.put(document)
            return document

        if self.runner is None:
            raise NumberingGenerationError(
                f"No cached numbering found and no runner configured for {pdb_id}."
            )

        contents = self.runner.generate(pdb_id)
        self.mapping_repository.save_text(pdb_id, self.numbering_name, contents)
        document = self.parser.parse(pdb_id, self.numbering_name, contents)
        self.cache.put(document)
        return document
