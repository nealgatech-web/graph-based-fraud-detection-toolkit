"""
fraudgraph.ml_model
-------------------
Train and apply a lightweight ML model (RandomForest) to estimate fraud probability
for each detected community.
"""

from __future__ import annotations
import numpy as np
import networkx as nx
from sklearn.ensemble import RandomForestClassifier
from typing import List, Set, Tuple, Dict


def extract_graph_features(G: nx.Graph, community: Set[str]) -> Dict[str, float]:
    """Compute simple structural features for a community subgraph."""
    H = G.subgraph(community)
    n = H.number_of_nodes()
    m = H.number_of_edges()
    density = 2 * m / (n * (n - 1)) if n > 1 else 0.0

    if isinstance(H, (nx.MultiGraph, nx.MultiDiGraph)):
        H = nx.Graph(H)

    tri = sum(nx.triangles(H).values()) / 3 if n > 2 else 0
    avg_deg = np.mean([deg for _, deg in H.degree()]) if n > 0 else 0
    max_deg = max([deg for _, deg in H.degree()], default=0)
    clustering = np.mean(list(nx.clustering(H).values())) if n > 2 else 0

    return dict(
        n_nodes=n,
        n_edges=m,
        density=density,
        tri=tri,
        avg_deg=avg_deg,
        max_deg=max_deg,
        clustering=clustering,
    )


def build_training_data(G: nx.Graph, ranked: List[Tuple[float, Set[str]]]) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """Generate (X, y, feature_names) from communities ranked by heuristics."""
    X, y = [], []
    for i, (score, community) in enumerate(ranked):
        feats = extract_graph_features(G, community)
        X.append(list(feats.values()))
        # Assume top-1 is fraudulent in synthetic data (weak supervision)
        y.append(1 if i == 0 else 0)
    return np.array(X), np.array(y), list(feats.keys())


def train_model(X: np.ndarray, y: np.ndarray) -> RandomForestClassifier:
    """Train a slightly deeper RandomForest model for more stable probabilities."""
    clf = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        max_depth=6,
        class_weight="balanced_subsample"
    )
    clf.fit(X, y)
    return clf


def predict_probabilities(clf: RandomForestClassifier, X: np.ndarray) -> np.ndarray:
    """Return fraud probabilities for each sample."""
    return clf.predict_proba(X)[:, 1]


def rank_with_ml(G: nx.Graph, ranked: List[Tuple[float, Set[str]]]) -> List[Tuple[float, Set[str], float]]:
    """
    Combine heuristic and ML-based suspicion:
      returns [(heuristic_score, community, ml_prob), ...] sorted by ml_prob descending.
    """
    X, y, feat_names = build_training_data(G, ranked)
    clf = train_model(X, y)
    probs = predict_probabilities(clf, X)
    combined = [
        (ranked[i][0], ranked[i][1], float(probs[i])) for i in range(len(ranked))
    ]
    return sorted(combined, key=lambda x: x[2], reverse=True)
