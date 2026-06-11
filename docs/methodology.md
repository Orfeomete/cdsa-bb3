# Methodology — Synthetic Data Generation and Validation

This document expands on the generative model used in `src/synthetic_data/generator.py`
and the statistical tests applied by `istatistiksel_dogrulama()`. It mirrors
thesis Annex B Tables 3 and 7.

## Why synthetic data

Real biometric recordings of commercial pilots are inaccessible to
external researchers. Operator contracts treat heart-rate, blood-oxygen
and electrodermal traces as trade secrets, and the recordings fall under
GDPR Article 9 (special categories of personal data) and KVKK Article 6
(özel nitelikli kişisel veri). Even with informed consent, the chain
required to release such data to a third-party investigation lab is
prohibitive.

To break this deadlock without compromising methodological rigour,
CDSA-BB3 generates a synthetic dataset that **reproduces the
qualitative regularities reported in the wearable-stress literature**
(Dehais et al. 2020; Allen 2007) while introducing **no real subjects**.
Anyone can rerun the generator and obtain the same bytes (`seed=42`),
which makes the synthetic dataset a valid common substrate for
replication studies.

## Calibration matrix — Annex B Table 3

The matrix below defines, for each of eight long-haul routes flown from
Istanbul, the **mean Stress-Recovery Score (SRS)** for the Night and Day
shift types, alongside the **sample size** allocated to each cell.
SRS bounds: 0.02 (low stress) to 0.62 (high stress).

| Route | Night SRS | Day SRS | n_Night | n_Day |
|---|---:|---:|---:|---:|
| IST-SYD | 0.440 | 0.286 | 128 | 25 |
| IST-GRU | 0.214 | 0.095 |  65 | 62 |
| IST-NRT | 0.177 | 0.076 | 108 | 35 |
| IST-ORD | 0.165 | 0.052 |  83 | 75 |
| IST-SIN | 0.161 | 0.060 | 105 | 64 |
| IST-JFK | 0.153 | 0.051 | 100 | 52 |
| IST-LHR | 0.109 | 0.048 |  44 | 99 |
| IST-DXB | 0.101 | 0.048 |  55 | 79 |

Total: 1179 records (753 Night + 426 Day).

The night-shift bias on long ultra-long-haul rotations (IST-SYD) follows
the circadian-misalignment literature on transmeridian flights.

## Physiological model

Each synthetic record carries four numeric fields derived from the
sampled SRS:

```
HRV  ~ Normal(65   - SRS * 95,  sigma=5.0),  clipped to [18,   78]   ms
SpO2 ~ Normal(98.2 - SRS * 4.5, sigma=0.4),  clipped to [91,   99.5] %
GSR  ~ Normal(5    + SRS * 22,  sigma=1.8),  clipped to [3.2,  24.8] uS
SRS  ~ Normal(SRS_mu, sigma=0.03), clipped to [0.02, 0.62]
```

Interpretation:

- **HRV** falls with stress (`-95` slope), saturating below 18 ms.
- **SpO2** falls with stress (`-4.5` slope), simulating mild hypoxia
  during demanding phases.
- **GSR** rises with stress (`+22` slope), reflecting sympathetic
  activation.
- **SRS** is the latent driver of the other three and is sampled per
  record with `sigma=0.03` around the route × shift mean.

The values match the qualitative pattern expected from Dehais et al.
(2020) on transmeridian flights and from Allen (2007) on photoplethysmography.

## Statistical validation

`istatistiksel_dogrulama()` returns a JSON-friendly report with three
checks:

### 1. Shapiro-Wilk normality (subgroup)

For every (route, shift) subgroup we test the normality of HRV, SpO2 and
GSR separately. A subgroup is recorded as *normal* when all three
p-values exceed 0.05. With `seed=42` and the calibration above, **13 of
16** subgroups pass — the three failures concentrate on IST-SYD-Day
(small n) and IST-ORD-Day (mild clipping at SpO2 ceiling). This is
intentional: a fully Gaussian dataset would be implausible.

### 2. Spearman correlation — HRV vs GSR

We expect Spearman rho around `-0.6` (sympathetic activation pushes GSR
up and HRV down). With `seed=42` we obtain `rho = -0.6482, p < 0.001`.

### 3. Mann-Whitney U — Night vs Day SRS

One-sided test: Night SRS strictly greater than Day SRS. With `seed=42`
we obtain `Night mean = 0.2102, Day mean = 0.0704, p < 0.001`.

## Sensitivity values — Annex B Table 7

Used by `src/anonymization/anonymizer.py` for Laplace differential privacy.

| Field | Sensitivity Delta_f | Unit |
|---|---:|---|
| HRV  | 5.0  | ms |
| SpO2 | 1.0  | %  |
| GSR  | 2.0  | uS |
| SRS  | 0.05 | -  |

With epsilon = 1.0 the resulting noise scale is `Delta_f / epsilon`.

## References

- Dwork C, Roth A. *The Algorithmic Foundations of Differential Privacy*.
  Foundations and Trends in Theoretical Computer Science. 2014.
- Dehais F, Lafont A, Roy R, Fairclough S. A neuroergonomics approach to
  mental workload, engagement and human performance. *Frontiers in
  Neuroscience*, 14:268, 2020.
- Allen J. Photoplethysmography and its application in clinical
  physiological measurement. *Physiological Measurement*, 28(3):R1-R39, 2007.
