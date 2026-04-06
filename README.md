# IgStrand-Align

IgStrand-Align maps immunoglobulin-domain structures into a shared IgStrand numbering space and exports both:

- `1D` residue-alignment tables
- `2D` topology-style Excel layouts based on domain templates

## Installation

Clone the repository, create a virtual environment, and install it in editable mode:

```bash
git clone https://github.com/umeshkhaniya/IgStrand-Align.git
cd IgStrand-Align
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
```

Core Python dependency:

- `openpyxl` for writing Excel output

External runtime dependency:

- `node` for generating new IgStrand numbering files when a structure is not already cached in `input/number_mapping_files/`

If you only use the bundled cached mapping files, Node is not required for those inputs.

## Example Input

Input files are whitespace-delimited with one domain request per line:

```text
1RHH B 1
5ESV D 1
```

Each line means:

- `PDB ID`
- `chain ID`
- `domain index` within that chain, using 1-based numbering after domain normalization

The repository includes a sample input file at [`src/input.txt`](./src/input.txt).

## Example Output

Typical outputs are written into [`output/`](./output):

- `1D_mapping_<input-stem>igstrand.xlsx`
- `2D_mapping_<input-stem>igstrand.xlsx`

For the bundled sample input, that means files like:

- `output/1D_mapping_inputigstrand.xlsx`
- `output/2D_mapping_inputigstrand.xlsx`

`1D` output contains one row per requested domain plus metadata columns such as reference structure, Ig type, TM-score, residue ranges, and one column for each IgStrand position.

`2D` output places each requested domain into a template-shaped panel, fills template numbering positions with residue identities, and preserves background coloring for loops and strand segments.

## CLI Usage

The new modular CLI is:

```bash
igstrand-align -f src/input.txt -d 1D
```

You can also invoke it directly with Python:

```bash
PYTHONPATH=src python3 -m igstrand_align.cli -f src/input.txt -d 1D,2D
```

Arguments:

- `-f`, `--file`: input file containing `PDB chain domain`
- `-d`, `--dimension`: one of `1D`, `2D`, or `1D,2D`

Examples:

```bash
igstrand-align -f src/input.txt -d 1D
igstrand-align -f src/input.txt -d 2D
igstrand-align -f src/input.txt -d 1D,2D
```

Output format:

- `1D` writes `xlsx`
- `2D` writes `xlsx`
- `pdf` is not implemented yet

The compatibility entry point still exists:

```bash
python3 src/main_script.py -f src/input.txt -d 1D,2D
```

That wrapper delegates to the modular package CLI, so both commands use the same implementation path.

## Algorithm

At a high level the pipeline works in four stages.

### 1. Numbering

For each requested PDB ID, the tool looks for a cached numbering file in `input/number_mapping_files/`.

- If the file exists, it is parsed directly.
- If it does not exist, the Node script [`src/refnum.js`](./src/refnum.js) is invoked to generate a new IgStrand numbering document using `icn3d`.

This numbering document contains:

- detected Ig-like domains
- the best matching reference structure
- alignment statistics such as TM-score and sequence identity
- per-residue IgStrand assignments

### 2. Domain Detection

The parser filters the numbering document down to the requested `PDB + chain`.

Each candidate domain is normalized by:

- parsing residue-to-IgStrand assignments
- extracting residue ranges
- mapping `refpdbname` to an Ig-domain class like `IgV`, `IgC1`, or `IgI`
- re-sorting domains by Ig-domain residue range so user-facing domain numbering is stable

### 3. 1D Alignment

For `1D` output, the tool:

- collects all IgStrand labels observed across the requested domains
- sorts them into a reproducible alignment order
- writes one spreadsheet row per domain
- fills each IgStrand column with the corresponding residue identity when present

Cells are color-coded by strand family, with loop positions highlighted separately.

### 4. 2D Alignment

For `2D` output, the tool:

- chooses an Excel template based on the domain class
- converts full IgStrand labels like `C'4548` into numeric template positions like `4548`
- overlays residue letters onto the template
- preserves template styling and shifts each rendered panel side-by-side into the output workbook

For `IgV` domains, template selection also checks whether the numbering contains strand `A`, strand `A'`, or both.

## Repository Layout

Key directories:

- [`src/igstrand_align`](./src/igstrand_align): modular package
- [`src/refnum.js`](./src/refnum.js): Node helper for generating new numbering files
- [`input/number_mapping_files`](./input/number_mapping_files): cached numbering JSON files
- [`input/igstrand_template`](./input/igstrand_template): 2D Excel templates
- [`output`](./output): generated workbooks

## Notes

- The modular package currently expects to run from a repository checkout because it uses the repository’s bundled templates and cached mapping files.
- `openpyxl` is required to write the Excel outputs.
