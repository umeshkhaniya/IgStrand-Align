"""Input parsing helpers."""

from pathlib import Path
from typing import Union

from ..core.exceptions import InputFormatError
from ..core.models import StructureRequest


def read_structure_requests(file_path: Union[str, Path]) -> list[StructureRequest]:
    """Read a whitespace-delimited input file into structure requests."""
    path = Path(file_path)
    if not path.exists():
        raise InputFormatError(f"Input file not found: {path}")

    requests: list[StructureRequest] = []
    with path.open() as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            fields = line.strip().split()
            if len(fields) != 3:
                raise InputFormatError(
                    f"Line {line_number} in {path} must contain exactly 3 fields: "
                    "PDB_ID CHAIN DOMAIN_INDEX."
                )

            try:
                domain_index = int(fields[2])
            except ValueError as exc:
                raise InputFormatError(
                    f"Line {line_number} in {path} has an invalid domain index: {fields[2]!r}"
                ) from exc

            requests.append(
                StructureRequest(
                    pdb_id=fields[0].upper(),
                    chain_id=fields[1],
                    domain_index=domain_index,
                )
            )

    if not requests:
        raise InputFormatError(f"Input file is empty: {path}")

    return requests
