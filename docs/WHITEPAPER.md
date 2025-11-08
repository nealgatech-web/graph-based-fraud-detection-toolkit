# FraudGraph Technical Summary

This document summarizes the problem, threat model, techniques, and reproducibility plan for **FraudGraph**.

## Problem
Collusive fraud often manifests as **rings** of accounts that share devices, payment instruments, or transaction patterns.
Traditional per-entity anomaly detection can miss these **network-level** signals.

## Approach
1. **ETL → Graph**: Convert flat events into a heterogeneous graph (accounts, devices/IPs/instruments). Multi-edges encode event type.
2. **Community detection (Louvain)**: highlight unusually dense/near-bipartite communities.
3. **Link analysis (HITS/PageRank)**: prioritize hubs/authorities within suspicious clusters.
4. **Suspicious subgraph scoring**:
   - Edge density & conductance
   - Triangles and 2-hop closure
   - Shared-identifier overlap (same device/ip/instrument across many accounts)
   - Temporal burstiness around events of interest

## Outputs
- Ranked communities with per-community diagnostics
- Node-level suspicion scores
- Markdown/CSV report for analysts

## Ethics & Safety
- Default to **synthetic data** in examples
- Strong separation of **signals** vs **actions**: this toolkit surfaces candidates; humans decide
- Documented risk of bias & false positives; encourage cross-signal corroboration

## Reproducibility
- Deterministic pipelines, seeds for graph generators
- Clear README with end-to-end commands
