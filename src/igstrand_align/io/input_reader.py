"""Input parsing helpers."""

from pathlib import Path
from typing import Union

from ..core.models import StructureRequest


def read_structure_requests(file_path: Union[str, Path]) -> list[StructureRequest]:
    """Read a whitespace-delimited input file into structure requests."""
    requests: list[StructureRequest] = []
    with open(file_path) as handle:
        for line in handle:
            if not line.strip():
                continue
            fields = line.strip().split()
            if len(fields) != 3:
                raise ValueError(f"Expected 3 fields per line, got: {fields}")
            requests.append(
                StructureRequest(
                    pdb_id=fields[0].upper(),
                    chain_id=fields[1],
                    domain_index=int(fields[2]),
                )
            )
    return requests
