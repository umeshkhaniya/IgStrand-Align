"""2D alignment builder."""

import re

from .models import Alignment2DPanel, Alignment2DResult


class Alignment2DBuilder:
    """Build template-oriented 2D alignment panels."""

    @staticmethod
    def _split_ig_label(number_string: str):
        match = re.search(r"^([^0-9]*)([0-9].*)$", number_string)
        return match.groups() if match else ("", number_string)

    @classmethod
    def _select_template_name(cls, domain):
        if domain.ig_type != "IgV":
            return domain.ig_type

        strands = {cls._split_ig_label(label)[0] for label in domain.residue_map}
        if "A" in strands and "A'" in strands:
            return "IgV_A_Adash"
        if "A'" in strands:
            return "IgV_Adash"
        if "A" in strands:
            return "IgV_A"
        return "IgV_A_Adash"

    def build(self, domains):
        panels = [
            Alignment2DPanel(
                domain=domain,
                template_name=self._select_template_name(domain),
                reference_structure=domain.ref_pdb_name,
            )
            for domain in domains
        ]
        return Alignment2DResult(panels=panels)
