# Traffic forecasting baseline repository proposal

The downloader and forecasting models should remain separate repositories connected by a versioned dataset contract.

## Why separate them

- The downloader owns authentication, source provenance, spatial selection and stable exports.
- The model repository owns splits, normalization, windows, training, evaluation and checkpoints.
- Users can update either side without installing PyTorch in the download utility.
- Experimental claims remain independent from website changes.

## Proposed repository

Suggested name:

```text
traffic-forecasting-baselines
```

Initial scope:

```text
configs/
datasets/
models/
  historical_average/
  rnn/
  gru/
  lstm/
  dcrnn/
  stgcn/
metrics/
scripts/
tests/
```

## Dataset contract

The first release should consume:

- `processed/observations.csv.gz`;
- `processed/stations.csv`;
- `processed/edges.csv`;
- `manifest.json`.

Preparation should produce versioned arrays:

```text
X: [sample, history, node, feature]
y: [sample, horizon, node, target]
mask: [sample, horizon, node]
```

## Baseline order

1. Last-value persistence.
2. Historical average.
3. Linear regression.
4. RNN, GRU and LSTM.
5. DCRNN and STGCN.
6. GE-GAN-compatible experiments.

Classical baselines are required. A deep model is not informative if it cannot beat persistence or historical average under the same split.

## Evaluation contract

- Split chronologically before fitting normalization.
- Fit scalers on training data only.
- Report MAE and RMSE; use masked MAPE only with an explicit low-flow policy.
- Evaluate 15, 30 and 60-minute horizons.
- Record random seeds, detector set, missing-data policy and git commit.
- Publish a dataset card and model card for every benchmark.

## Recommended first milestone

Implement one documented PeMS sample pipeline and four baselines:

```text
Historical Average → Persistence → GRU → LSTM
```

Only add graph models after the adjacency semantics and detector coverage have been validated.

