# Reproducibility Scripts

This directory contains scripts for reproducible research workflows.

## Directory Structure

```
scripts/
├── matrix_orchestration/    # Full-matrix experiment execution
├── aggregation/              # Result aggregation and deliverables
├── analysis/                 # Statistical analysis and figure generation
├── validation/               # Quality control and verification
└── reproducibility/          # End-to-end pipeline orchestration
```

## Status

⚠️ **Scripts are not yet implemented.**

This is a placeholder structure for future reproducibility-first workflow implementation.

## Planned Scripts

### Matrix Orchestration
- `generate_manifest.py` - Generate pre-execution experiment manifest
- `run_matrix.py` - Execute full factorial matrix (4 strategies × 8 scenarios × 3 seeds)
- `verify_completion.py` - Verify all runs completed successfully

### Aggregation
- `aggregate_results.py` - Combine raw results into structured tables
- `generate_deliverables.py` - Create experiment_results.csv and related deliverables

### Analysis
- `statistical_analysis.py` - Perform Friedman + Wilcoxon + Holm correction
- `generate_figures.py` - Generate publication-quality figures (7 figures)
- `descriptive_stats.py` - Compute descriptive statistics

### Validation
- `qc_checks.py` - Run 14 quality control checks
- `validate_configuration.py` - Pre-run configuration validation
- `verify_results.py` - Post-run result verification

### Reproducibility
- `full_pipeline.py` - End-to-end orchestration (all stages)
- `provenance_report.py` - Generate complete provenance documentation
- `checksum_verification.py` - Verify data integrity

## Design Principles

All scripts must:
1. Accept command-line arguments (no hardcoded paths)
2. Validate inputs before execution
3. Log actions to stdout/stderr
4. Return meaningful exit codes (0=success)
5. Generate structured outputs (JSON + Markdown)
6. Record complete provenance
7. Be idempotent where possible
8. Be deterministic (same inputs → same outputs)

## Current Single-Run Workflow

Until scripts are implemented, single runs can be executed via:

```bash
python -m experiments.runner \
  --strategy proposed \
  --scenario gradual_drift \
  --seed 42 \
  --stream-mode interleaved \
  --stream-length 2400 \
  --scenario-onset-cycle-min 25 \
  --scenario-onset-cycle-max 35
```

See `experiments/README.md` for details.
