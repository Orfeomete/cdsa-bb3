# Contributing to CDSA-BB3

Thank you for your interest. CDSA-BB3 is an academic prototype
supporting a doctoral thesis, so contribution scope is intentionally
narrow. We welcome the following.

## What we welcome

- **Bug reports** in the synthetic data, anonymization, or cryptographic
  modules.
- **Reproducibility issues** — if `python examples/quick_start.py` does
  not produce the expected verbatim output, please open an issue and
  include your Python version, OS, NumPy / SciPy / cryptography versions,
  and the actual output you observed.
- **Documentation improvements** — clarifications, typo fixes, missing
  references.
- **Replication studies** — if you reproduce results from the paper on
  an independent dataset, please open a Discussion thread so we can link
  to your work.

## What we do not accept

- **Real biometric data** — the project is built on a data-locality
  principle. Pull requests that introduce real-pilot recordings will be
  closed without merge.
- **Cryptographic algorithm replacements** — Module 3 is a documented
  implementation of the thesis architecture. Substituting another scheme
  is out of scope for v1.x; please open a Discussion for v2.x candidates.
- **Production cryptography claims** — please do not market this prototype
  as production-grade. It is a pedagogical reference for the thesis.

## How to contribute

1. Open an issue first to discuss the change.
2. Fork, branch (`fix/issue-NN` or `docs/topic`), commit with
   imperative messages, push.
3. Open a pull request referencing the issue. Tests must pass
   (`pytest tests/`).

## Authorship policy

Per the **Authorship and Citation Rule** (frozen decision, 15 May 2026),
the doctoral supervisor is named only on the thesis manuscript. External
contributors who substantively improve the code or documentation will
be acknowledged in the project's `CHANGELOG.md` and (where relevant) in
any derived publication's Acknowledgements section, subject to ICMJE
authorship criteria.

## Code style

- Python 3.10+.
- NumPy / SciPy / cryptography only — no new heavy dependencies.
- Docstrings in NumPy / SciPy style.
- Function and variable names may be Turkish for parity with the thesis
  (e.g., `veri_uret`, `anonimize_et`); module-level comments and
  docstrings are English.

## Reporting security issues

Cryptographic concerns should be reported privately by email to
`metecantekin@gmail.com` rather than in a public issue.
