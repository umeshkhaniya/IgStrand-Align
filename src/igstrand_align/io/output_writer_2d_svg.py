"""Native SVG writer for 2D topology-style output."""

from collections import OrderedDict
from html import escape
from pathlib import Path
import re

from ..alignment.color_rules import STRAND_COLOR_MAP_1D


class OutputWriter2DSvg:
    """Render 2D alignment panels as a standalone SVG document."""

    panel_width = 920
    panel_padding = 24
    row_height = 38
    cell_width = 42
    header_height = 96
    footer_height = 26
    panel_gap = 28

    @staticmethod
    def _split_ig_label(number_string: str):
        match = re.search(r"^([^0-9]*)([0-9].*)$", number_string)
        return match.groups() if match else ("", number_string)

    @classmethod
    def _sort_key(cls, ig_label: str):
        _, numeric = cls._split_ig_label(ig_label)
        tokens = re.findall(r"\d+|\D+", numeric)
        return tuple(int(token) if token.isdigit() else token for token in tokens)

    @classmethod
    def _group_residues(cls, residue_map):
        grouped = OrderedDict()
        for ig_label in sorted(residue_map, key=cls._sort_key):
            strand, _ = cls._split_ig_label(ig_label)
            grouped.setdefault(strand or "?", []).append(residue_map[ig_label])
        return grouped

    @classmethod
    def _fill_color(cls, residue_mapping):
        if residue_mapping.is_loop:
            return STRAND_COLOR_MAP_1D["loop"]
        if residue_mapping.ig_label.endswith("50"):
            return "FFD700"
        strand = cls._split_ig_label(residue_mapping.ig_label)[0]
        return STRAND_COLOR_MAP_1D.get(strand, "FFFFFF")

    def _panel_height(self, panel):
        grouped = self._group_residues(panel.domain.residue_map)
        return self.header_height + len(grouped) * self.row_height + self.footer_height

    def _render_panel(self, panel, x_offset: int, y_offset: int):
        grouped = self._group_residues(panel.domain.residue_map)
        panel_height = self._panel_height(panel)
        parts = [
            f'<g transform="translate({x_offset},{y_offset})">',
            (
                f'<rect x="0" y="0" width="{self.panel_width}" height="{panel_height}" '
                'rx="18" fill="#fffdfa" stroke="#cbbfa6" stroke-width="2"/>'
            ),
            (
                f'<text x="{self.panel_padding}" y="30" font-family="Helvetica, Arial, sans-serif" '
                'font-size="24" font-weight="700" fill="#2a2117">'
                f'{escape(panel.domain.structure_id)}</text>'
            ),
            (
                f'<text x="{self.panel_padding}" y="56" font-family="Helvetica, Arial, sans-serif" '
                'font-size="16" fill="#574838">'
                f'Ig type: {escape(panel.domain.ig_type)} | Template: {escape(panel.template_name)}</text>'
            ),
            (
                f'<text x="{self.panel_padding}" y="78" font-family="Helvetica, Arial, sans-serif" '
                'font-size="14" fill="#6f604f">'
                f'Reference: {escape(panel.reference_structure)}</text>'
            ),
        ]

        y = self.header_height
        for strand, residues in grouped.items():
            parts.append(
                (
                    f'<text x="{self.panel_padding}" y="{y + 24}" '
                    'font-family="Helvetica, Arial, sans-serif" font-size="16" '
                    'font-weight="700" fill="#3b3228">'
                    f'{escape(strand)}</text>'
                )
            )
            x = self.panel_padding + 56
            for residue in residues:
                fill = self._fill_color(residue)
                parts.append(
                    (
                        f'<rect x="{x}" y="{y}" width="{self.cell_width}" height="28" rx="6" '
                        f'fill="#{fill}" stroke="#8d7e6f" stroke-width="1"/>'
                    )
                )
                parts.append(
                    (
                        f'<text x="{x + self.cell_width / 2}" y="{y + 18}" '
                        'text-anchor="middle" font-family="Menlo, Consolas, monospace" '
                        'font-size="13" font-weight="700" fill="#1d1a17">'
                        f'{escape(residue.residue_code)}</text>'
                    )
                )
                x += self.cell_width + 6
            y += self.row_height

        footer_y = panel_height - 10
        parts.append(
            (
                f'<text x="{self.panel_padding}" y="{footer_y}" '
                'font-family="Helvetica, Arial, sans-serif" font-size="12" fill="#7b6d5d">'
                f'3D range: {escape(panel.domain.domain_residue_range)} | '
                f'Ig range: {escape(panel.domain.ig_residue_range)}</text>'
            )
        )
        parts.append("</g>")
        return "\n".join(parts), panel_height

    def write(self, result, destination):
        panel_heights = [self._panel_height(panel) for panel in result.panels] or [200]
        total_height = sum(panel_heights) + self.panel_gap * (len(panel_heights) - 1) + 40
        total_width = self.panel_width + 40
        y = 20
        body_parts = []

        for panel in result.panels:
            panel_svg, panel_height = self._render_panel(panel, 20, y)
            body_parts.append(panel_svg)
            y += panel_height + self.panel_gap

        svg = "\n".join(
            [
                '<?xml version="1.0" encoding="UTF-8"?>',
                (
                    f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" '
                    f'height="{total_height}" viewBox="0 0 {total_width} {total_height}">'
                ),
                '<rect width="100%" height="100%" fill="#f6f1e8"/>',
                *body_parts,
                "</svg>",
            ]
        )

        output_path = Path(destination)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(svg)
        return output_path
