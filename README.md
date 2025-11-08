# FraudGraph: Transaction & Graph-based Fraud Detection Toolkit

**FraudGraph** is an open-source toolkit to build transaction networks from event logs and run scalable graph algorithms —
community detection, link analysis, and suspicious subgraph scoring — to surface **collusive fraud rings**.

## Why this matters
Large fraud schemes are rarely isolated. They behave like **networks**: coordinated accounts, shared devices, and recycled payment instruments.
Finding the **ring** (not just the bad individual) helps platforms, investigators, and researchers stop coordinated attacks and reduce harm at scale.

## Features
- **ETL → Graph**: From flat events to a heterogeneous network (users, devices, cards, IPs) with typed edges.
- **Algorithms**:
  - Louvain community detection
  - HITS / PageRank-style authority-hub analysis
  - Suspicious subgraph scoring (density, triads, shared-identifier overlap, burstiness)
- **Scalable paths**:
  - Prototype with **NetworkX**
  - Optional connector to **Neo4j** for larger graphs (Cypher + APOC friendly)
- **Reproducible demos**: Jupyter notebook and an end-to-end example with a **simulated collusive ring**.
- **Ethics & Safety by design**: Clear docs on anonymization, differential risk of false positives, and reproducibility.

## Quickstart

```bash
# 1) Install (recommended: Python 3.10+)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt  # or: pip install -e .
# 2) Run the simulated example
python examples/simulate_ring.py --out data/sim_transactions.csv
python examples/run_pipeline.py --transactions data/sim_transactions.csv --out reports
# 3) Open the demo notebook
# jupyter lab notebooks/demo_ring.ipynb
```

## Data
- **Synthetic** by default (provided script) to avoid handling real PII.
- You can also point the ETL to public research datasets that include transaction-like edges (e.g., anonymized credit-card fraud
  samples, synthetic fintech traces). Always ensure proper licensing and anonymization.

## Project layout
```
fraudgraph-toolkit/
├─ src/fraudgraph/
│  ├─ etl.py                  # Build graphs from CSV/JSONL transactions
│  ├─ algorithms.py           # Louvain, HITS, suspicious subgraph scoring
│  └─ connectors/
│     └─ neo4j_connector.py   # Example writer/reader to Neo4j
├─ examples/
│  ├─ simulate_ring.py        # Generate synthetic ring & benign background
│  └─ run_pipeline.py         # CLI: ETL → algorithms → markdown report
├─ notebooks/
│  └─ demo_ring.ipynb         # Walkthrough & visualizations
├─ docs/
│  └─ WHITEPAPER.md           # Short, non-marketing technical summary
├─ data/                      # (gitignored) place local inputs here
└─ README.md
```

## Reproducing the case study
1. Generate or supply a CSV of transactions with columns:
   - `timestamp, sender, receiver, amount, device_id, ip, instrument_id`
2. Run the pipeline (see above) to create a graph and produce a lightweight report with top communities and scores.
3. Inspect the notebook for visual exploration and parameter tuning.

## Societal impact
This toolkit supports research and engineering work to **reduce large-scale coordinated financial scams** by
highlighting suspicious clusters for deeper human review. It **does not** perform automated bans; it provides signals
to assist analysts and investigators.

## Contributing
Issues and PRs are welcome! See **docs/WHITEPAPER.md** for the threat model and **CONTRIBUTING** notes inside the README.

## License
MIT (see `LICENSE`).
