from __future__ import annotations
import math
import networkx as nx
from typing import Dict, List, Tuple, Iterable
from collections import defaultdict

def louvain_communities(G: nx.Graph, resolution: float = 1.0, seed: int = 0) -> List[set]:
    """
    Louvain on an undirected view of the graph. Requires networkx >= 3.0 with community.louvain_communities.
    MultiDiGraph is projected to simple undirected by ignoring edge direction and multi-edges for modularity.
    """
    if isinstance(G, (nx.MultiGraph, nx.MultiDiGraph)):
        H = nx.Graph()
        for u, v in G.edges():
            H.add_edge(u, v)
    else:
        H = G.copy().to_undirected()

    try:
        from networkx.algorithms.community import louvain_communities
        return list(louvain_communities(H, resolution=resolution, seed=seed))
    except Exception as e:
        raise RuntimeError("Louvain requires networkx >= 3.0 (community.louvain_communities).") from e

def hits_scores(G: nx.DiGraph, max_iter: int = 100) -> Tuple[Dict, Dict]:
    """Compute HITS scores on a directed view of the graph."""
    if isinstance(G, nx.MultiDiGraph):
        H = nx.DiGraph()
        for u, v in G.edges():
            H.add_edge(u, v)
    else:
        H = G.copy().to_directed()
    hubs, auth = nx.hits(H, max_iter=max_iter, normalized=True)
    return hubs, auth

def suspicious_subgraph_score(G: nx.Graph, nodes: Iterable) -> float:
    """
    Simple composite score for a subgraph induced by `nodes`:
      - density (higher is worse)
      - low conductance (lower is worse) -> invert contribution
      - triangle rate (higher can indicate tight collusion)
    All terms min-max normalized by simple heuristics.
    """
    H = G.subgraph(nodes).copy()
    if H.number_of_nodes() <= 1:
        return 0.0
    # Undirected simple view
    if isinstance(H, (nx.MultiGraph, nx.MultiDiGraph)):
        H = nx.Graph(H)
    n = H.number_of_nodes()
    m = H.number_of_edges()
    density = 2*m / (n*(n-1)) if n > 1 else 0.0

    # Conductance: edges leaving / (2m + edges leaving); approximate via cut size to complement
    cut_edges = 0
    node_set = set(H.nodes())
    for u, v in G.edges():
        if (u in node_set) ^ (v in node_set):
            cut_edges += 1
    conductance = cut_edges / (2*m + cut_edges) if (2*m + cut_edges) > 0 else 1.0
    inv_conductance = 1.0 - conductance

    # Triangle rate
    tri = sum(nx.triangles(H).values()) / 3
    max_tri = n*(n-1)*(n-2)/6 if n >= 3 else 1.0
    tri_rate = tri / max_tri

    # Composite (weights can be tuned)
    score = 0.5*density + 0.3*inv_conductance + 0.2*tri_rate
    return float(score)

def rank_communities_by_suspicion(G: nx.Graph, communities: List[set]) -> List[Tuple[float, set]]:
    ranked = []
    for com in communities:
        ranked.append((suspicious_subgraph_score(G, com), com))
    return sorted(ranked, key=lambda x: x[0], reverse=True)
