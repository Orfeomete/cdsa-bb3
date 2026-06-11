# Documentation Index

This directory holds reference documents that accompany the
CDSA-BB3 source code.

## Files

| File | Purpose |
|---|---|
| `arXiv_preprint.pdf` | Rendered preprint (21 pages, Beykent imprint). Identical to the LaTeX source in `paper/`. |
| `methodology.md` | Narrative walk-through of Annex B Table 3 (route × shift calibration matrix) and Annex B Table 7 (sensitivity values used by Laplace differential privacy). |
| `cryptography_notes.md` | Notes on NIST SP 800-38D (AES-GCM) and Shamir (1979) as applied in Module 3, including AAD format and Lagrange reconstruction. |

## Cross-references

- LaTeX submission package: `../paper/main.tex` + `../paper/references.bib` + `../paper/images/`
- Source code: `../src/synthetic_data/` + `../src/anonymization/` + `../src/cryptography/`
- Examples: `../examples/quick_start.py` + `../examples/reproduce_thesis.py`
- Tests: `../tests/test_prototype.py`

## How to read

For a quick orientation, read in this order:

1. `../README.md` — project overview, layout, quick start.
2. `methodology.md` — generative model and statistical validation rationale.
3. `arXiv_preprint.pdf` — full academic narrative (21 pages).
4. `cryptography_notes.md` — cryptographic design choices.
5. `../src/` — implementation, with module-level docstrings.
