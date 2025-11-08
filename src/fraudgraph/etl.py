from __future__ import annotations
import pandas as pd
import networkx as nx
from typing import Iterable, Optional, Dict, Any

EDGE_TYPES = ("txn", "device_link", "ip_link", "instrument_link")

def load_transactions(path: str) -> pd.DataFrame:
    """Load a CSV with columns: timestamp, sender, receiver, amount, device_id, ip, instrument_id"""
    df = pd.read_csv(path)
    required = {"timestamp", "sender", "receiver", "amount"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df

def build_graph(df: pd.DataFrame, include_id_links: bool = True) -> nx.MultiDiGraph:
    """
    Build a heterogeneous MultiDiGraph:
      - Nodes: account:<id>, device:<id>, ip:<ip>, instrument:<id>
      - Edges: txn(sender->receiver), device_link(account<->device), ip_link(account<->ip), instrument_link(account<->instrument)
    """
    G = nx.MultiDiGraph()
    # Add transaction edges
    for row in df.itertuples(index=False):
        a = f"account:{getattr(row,'sender')}"
        b = f"account:{getattr(row,'receiver')}"
        G.add_node(a, type="account")
        G.add_node(b, type="account")
        G.add_edge(a, b, key="txn", type="txn",
                   amount=float(getattr(row,'amount', 0.0)),
                   timestamp=getattr(row,'timestamp', None))
        if include_id_links:
            if hasattr(row, "device_id") and pd.notna(row.device_id):
                d = f"device:{row.device_id}"
                G.add_node(d, type="device")
                G.add_edge(a, d, key="device_link", type="device_link")
                G.add_edge(b, d, key="device_link", type="device_link")
            if hasattr(row, "ip") and pd.notna(row.ip):
                ipn = f"ip:{row.ip}"
                G.add_node(ipn, type="ip")
                G.add_edge(a, ipn, key="ip_link", type="ip_link")
                G.add_edge(b, ipn, key="ip_link", type="ip_link")
            if hasattr(row, "instrument_id") and pd.notna(row.instrument_id):
                instr = f"instrument:{row.instrument_id}"
                G.add_node(instr, type="instrument")
                G.add_edge(a, instr, key="instrument_link", type="instrument_link")
                G.add_edge(b, instr, key="instrument_link", type="instrument_link")
    return G
