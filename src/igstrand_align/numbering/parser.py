"""Parsers for cached numbering files."""

import json
import re

from .models import RawNumberingDocument


class NumberingParser:
    """Parse raw numbering payloads into structured Python objects."""

    def parse(self, pdb_id: str, numbering_name: str, contents: str) -> RawNumberingDocument:
        normalized = contents.rstrip("\n")
        if normalized and not normalized.endswith("]"):
            normalized += "]"

        # Cached refnum files are close to JSON, but may contain trailing commas.
        normalized = re.sub(r",(\s*[}\]])", r"\1", normalized)

        parsed = json.loads(normalized) if normalized else []
        return RawNumberingDocument(
            pdb_id=pdb_id,
            numbering_name=numbering_name,
            content=contents,
            parsed=parsed,
        )
