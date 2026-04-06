"""Domain selection and normalization."""

import re

from ..core.exceptions import DomainNotFoundError
from ..core.models import DomainRecord, ResidueMapping, StructureRequest

REF_TO_IG_TYPE = {
    "ASF1A_2iijA_human": "IgE",
    "B2Microglobulin_7phrL_human_C1": "IgC1",
    "BArrestin1_4jqiA_rat_n1": "IgFN3-like",
    "BTLA_2aw2A_human_Iset": "IgI",
    "C3_2qkiD_human_n1": "IgFN3-like",
    "CD19_6al5A_human-n1": "CD19",
    "CD28_1yjdC_human_V": "IgV",
    "CD2_1hnfA_human_C2-n2": "IgC2",
    "CD2_1hnfA_human_V-n1": "IgV",
    "CD3d_6jxrd_human_C1": "IgC1",
    "CD3e_6jxrf_human_C1": "IgC1",
    "CD3g_6jxrg_human_C2": "IgC2",
    "CD8a_1cd8A_human_V": "IgV",
    "CoAtomerGamma1_1r4xA_human": "IgE",
    "Contactin1_2ee2A_human_FN3-n9": "IgFN3",
    "Contactin1_3s97C_human_Iset-n2": "IgI",
    "CuZnSuperoxideDismutase_1hl5C_human": "SOD",
    "ECadherin_4zt1A_human_n2": "Cadherin",
    "Endo-1,4-BetaXylanase10A_1i8aA_bacteria_n4": "IgE",
    "FAB-HEAVY_5esv_C1-n2": "IgC1",
    "FAB-HEAVY_5esv_V-n1": "IgV",
    "FAB-LIGHT_5esv_C1-n2": "IgC1",
    "FAB-LIGHT_5esv_V-n1": "IgV",
    "GHR_1axiB_human_C1-n1": "IgC1",
    "ICOS_6x4gA_human_V": "IgV",
    "IL6Rb_1bquB_human_FN3-n2": "IgFN3",
    "IL6Rb_1bquB_human_FN3-n3": "IgFN3",
    "InsulinR_8guyE_human_FN3-n1": "IgFN3",
    "InsulinR_8guyE_human_FN3-n2": "IgFN3",
    "IsdA_2iteA_bacteria": "IgE",
    "JAM1_1nbqA_human_Iset-n2": "IgI",
    "LAG3_7tzgD_human_C1-n2": "IgC1",
    "LAG3_7tzgD_human_V-n1": "IgV",
    "LaminAC_1ifrA_human": "Lamin",
    "MHCIa_7phrH_human_C1": "IgC1",
    "MPT63_1lmiA_bacteria": "IgE",
    "NaCaExchanger_2fwuA_dog_n2": "IgFN3-like",
    "NaKATPaseTransporterBeta_2zxeB_spurdogshark": "IgE",
    "ORF7a_1xakA_virus": "ORF",
    "PD1_4zqkB_human_V": "IgV",
    "PDL1_4z18B_human_V-n1": "IgV",
    "Palladin_2dm3A_human_Iset-n1": "IgI",
    "RBPJ_6py8C_human_Unk-n1": "IgFN3-like",
    "RBPJ_6py8C_human_Unk-n2": "IgFN3-like",
    "Sidekick2_1wf5A_human_FN3-n7": "IgFN3",
    "Siglec3_5j0bB_human_C1-n2": "IgC1",
    "TCRa_6jxrm_human_C1-n2": "IgC1",
    "TCRa_6jxrm_human_V-n1": "IgV",
    "TEAD1_3kysC_human": "IgE",
    "TP34_2o6cA_bacteria": "IgE",
    "TP47_1o75A_bacteria": "IgE",
    "Titin_4uowM_human_Iset-n152": "IgI",
    "VISTA_6oilA_human_V": "IgV",
    "VNAR_1t6vN_shark_V": "IgV",
    "VTCN1_Q7Z7D3_human_C1-n2": "IgC1",
}


class DomainDetector:
    """Select and normalize a requested domain from a numbering document."""

    @staticmethod
    def _sort_residue_range(item_dict, residue_range: str):
        match = re.match(r"(\d+)([a-zA-Z]?):(\d+)([a-zA-Z]?)", item_dict[residue_range])
        if not match:
            return float("inf"), float("inf")

        start_num, start_alpha, end_num, end_alpha = match.groups()
        start = int(start_num)
        end = int(end_num)
        if start_alpha:
            start += ord(start_alpha.lower()) - ord("a") + 1
        if end_alpha:
            end += ord(end_alpha.lower()) - ord("a") + 1
        return start, end

    @staticmethod
    def _parse_igmapinfo(igstrand_data):
        residue_map: dict[str, ResidueMapping] = {}
        undefined_residues: list[str] = []

        first_identity = next(iter(igstrand_data[0].keys()))
        last_identity = next(iter(igstrand_data[-1].keys()))
        ig_domain_start = first_identity.split("_")[2]
        ig_domain_end = last_identity.split("_")[2]

        for ig_num_info in igstrand_data:
            residue_identity, strand_number = next(iter(ig_num_info.items()))
            residue_parts = residue_identity.split("_")
            residue_letter = residue_parts[-1]
            residue_number = residue_parts[2]

            if strand_number == "undefined":
                undefined_residues.append(residue_number)
                continue

            strand_tokens = strand_number.split("_")
            ig_label = strand_tokens[0]
            is_loop = len(strand_tokens) == 2 and strand_tokens[1] == "loop"

            if ig_label not in residue_map:
                residue_map[ig_label] = ResidueMapping(
                    ig_label=ig_label,
                    residue_code=residue_letter,
                    is_loop=is_loop,
                )

        return residue_map, f"{ig_domain_start}:{ig_domain_end}", undefined_residues

    def _iter_domain_candidates(self, numbering_document, request: StructureRequest):
        pdb_id = request.pdb_id.upper()
        chain_key = f"{pdb_id}_{request.chain_id}"

        for item in numbering_document.parsed:
            if pdb_id not in item:
                continue
            pdb_payload = item[pdb_id]
            if pdb_payload.get("Ig domain") != 1:
                continue
            for ig_entry in pdb_payload.get("igs", []):
                if chain_key not in ig_entry:
                    continue
                chain_data = ig_entry[chain_key]
                for id_chain_3d, ref_ig_data in chain_data.items():
                    _, domain_info = id_chain_3d.split(",")
                    domain_residue_info = domain_info.split("_")
                    domain_order = int(domain_residue_info[0]) + 1
                    domain_residue_range = ":".join(domain_residue_info[1].split(":")[0:2])
                    residue_map, ig_residue_range, undefined_residues = self._parse_igmapinfo(
                        ref_ig_data["data"]
                    )
                    yield {
                        "structure_id": f"{chain_key}_{domain_order}",
                        "ref_pdb_name": ref_ig_data["refpdbname"],
                        "ig_type": REF_TO_IG_TYPE.get(ref_ig_data["refpdbname"], ""),
                        "domain_order": domain_order,
                        "domain_residue_range": domain_residue_range,
                        "ig_residue_range": ig_residue_range,
                        "tm_score": ref_ig_data.get("score"),
                        "seq_id": ref_ig_data.get("seqid"),
                        "n_res_aligned": ref_ig_data.get("nresAlign"),
                        "undefined_residues": undefined_residues,
                        "residue_map": residue_map,
                    }

    def select_domain(self, numbering_document, request: StructureRequest) -> DomainRecord:
        if numbering_document is None:
            raise DomainNotFoundError(
                f"No numbering document available for {request.pdb_id}."
            )

        candidates = sorted(
            self._iter_domain_candidates(numbering_document, request),
            key=lambda item: self._sort_residue_range(item, "ig_residue_range"),
        )
        for index, candidate in enumerate(candidates, start=1):
            candidate["structure_id"] = f"{request.pdb_id}_{request.chain_id}_{index}"
            candidate["domain_order"] = index
            if index == request.domain_index:
                return DomainRecord(**candidate)

        raise DomainNotFoundError(
            f"Could not resolve domain {request.domain_index} for "
            f"{request.pdb_id}_{request.chain_id}."
        )
