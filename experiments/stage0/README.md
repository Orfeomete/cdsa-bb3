# Stage 0 and Stage 0b evidence-integrity studies

Scripts and result files of the two preregistered studies reported in the companion feasibility paper, together with
the analyses that were not preregistered. The preregistrations are in `docs/preregistration/`.

| File | Role |
|---|---|
| `stage0_kosum_v1.py` | Stage 0 run, MIT-BIH record 100, seed 20260823, preregistered 23 August 2026 |
| `stage0b_kosum_v1.py` | Stage 0b run, MIT-BIH record 234 and BIDMC bidmc01, seed 20260910, preregistered 10 September 2026 |
| `c_akis_butunlugu_testi.py` | Stream manipulation test, published verifier against a verifier with added checks, not preregistered |
| `desen_tohum_taramasi.py` | Seed sweep over seeds 0 to 1999, not preregistered |
| `tek_pay_denetimi.py` | Post-hoc single-share check, 14 October 2026, not preregistered |
| `patlamali_kayip_modeli.py` | Exploratory burst-loss model, seed 20261014, not preregistered |

The scripts were run from the project layout in which this repository sits at `../12_GitHub_Repo/cdsa-bb3` relative to
the study folder, and they import `src.cryptography` from there. Raw PhysioNet files are not redistributed. The scripts
download them, and their sizes and SHA-256 digests are recorded in the result files and in
`results/PHYSIONET_OFFICIAL_DIGESTS.txt`.

Known departures from the preregistrations are documented in the paper. The single-share criterion was written into
both run scripts as a constant and was checked afterwards by `tek_pay_denetimi.py`. Latencies are single timings per
wrapper call. The associated data bind the scenario label, the packet identifier and a format tag. The 28-byte overhead
is a constant. The runs used the Shamir sampler of release 2.2.0, which drew the coefficient from 256 bits, while the
cryptographic modules were otherwise identical to commit a659c4b.
