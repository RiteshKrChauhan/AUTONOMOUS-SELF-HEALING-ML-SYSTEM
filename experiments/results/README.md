# Experiment Results

This directory contains experimental results from the research framework.

## Directory Structure

```
results/
├── raw/                    # Event-level CSV files (one per run)
├── aggregated/             # Summary JSON files (one per run)
└── figures/                # Generated visualizations
```

## Current Status

✅ **Directory structure created**  
⚠️ **No current experiment results**

Previous research artifacts (96-run valid matrix, invalid matrix) have been archived externally and removed from the working repository to establish a clean baseline for reproducibility-first workflows.

## Archived Results

Previous experimental artifacts are preserved in:
```
E:\Capstone Projects\AUTONOMOUS_ML_ARCHIVE_20260824\
```

See `ARCHIVE_RESTORE_VERIFICATION.md` (in archive) for complete inventory.

## Future Results

New experimental results will be generated using reproducibility scripts in `scripts/` (not yet implemented).

Expected structure for future matrix runs:

```
results/
├── matrix_YYYYMMDD_HHMMSS/
│   ├── experiment_manifest.csv
│   ├── experiment_results.csv
│   ├── matrix_execution_log.json
│   ├── qc_status.json
│   ├── PROVENANCE_REPORT.md
│   ├── raw/
│   │   ├── {run_id}_events.csv (96 files)
│   ├── aggregated/
│   │   ├── {run_id}_summary.json (96 files)
│   ├── statistical_analysis/
│   │   ├── *.csv (7 files)
│   │   ├── *.md (reports)
│   │   └── figures/
│   │       └── *.png (7 figures)
```

## Run ID Format

Run IDs are deterministic:
```
{strategy}_{scenario}_seed{seed}
```

Examples:
- `static_gradual_drift_seed42`
- `proposed_sudden_spike_seed123`
- `scheduled_high_noise_seed456`

## Single-Run Execution

To execute a single experimental run:

```bash
python -m experiments.runner \
  --strategy proposed \
  --scenario gradual_drift \
  --seed 42 \
  --stream-mode interleaved \
  --stream-length 2400
```

Results are written to:
- `raw/{run_id}_{timestamp}_events.csv`
- `aggregated/{run_id}_{timestamp}_summary.json`

See `experiments/README.md` for full documentation.
