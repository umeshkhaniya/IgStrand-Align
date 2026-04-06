"""1D alignment builder."""

import re

from .models import Alignment1DResult


class Alignment1DBuilder:
    """Build a normalized 1D alignment view across multiple domains."""

    @staticmethod
    def _split_ig_label(number_string: str):
        match = re.search(r"^([^0-9]*)([0-9].*)$", number_string)
        return match.groups() if match else ("", number_string)

    @classmethod
    def _sort_key(cls, ig_label: str):
        _, numeric = cls._split_ig_label(ig_label)
        tokens = re.findall(r"\d+|\D+", numeric)
        return tuple(int(token) if token.isdigit() else token for token in tokens)

    def build(self, domains):
        ig_labels = sorted(
            {label for domain in domains for label in domain.residue_map},
            key=self._sort_key,
        )
        return Alignment1DResult(domains=list(domains), ig_labels=ig_labels)
