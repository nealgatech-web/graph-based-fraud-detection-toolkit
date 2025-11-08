import argparse, os, csv
import networkx as nx
from fraudgraph.etl import load_transactions, build_graph
from fraudgraph.algorithms import louvain_communities, hits_scores, rank_communities_by_suspicion

def write_report(out_dir, ranked):
    os.makedirs(out_dir, exist_ok=True)
    md_path = os.path.join(out_dir, "report.md")
    with open(md_path, "w") as f:
        f.write("# FraudGraph Report\n\n")
        for i, (score, nodes) in enumerate(ranked[:10], 1):
            f.write(f"## Community {i} — Suspicion Score: {score:.3f}\n")
            acc = [n for n in nodes if str(n).startswith("account:")]
            dev = [n for n in nodes if str(n).startswith("device:")]
            ip = [n for n in nodes if str(n).startswith("ip:")]
            instr = [n for n in nodes if str(n).startswith("instrument:")]
            f.write(f"- Accounts: {len(acc)}, Devices: {len(dev)}, IPs: {len(ip)}, Instruments: {len(instr)}\n\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--transactions", required=True)
    ap.add_argument("--out", default="reports")
    args = ap.parse_args()

    df = load_transactions(args.transactions)
    G = build_graph(df, include_id_links=True)
    comms = louvain_communities(G)
    ranked = rank_communities_by_suspicion(G, comms)
    hubs, auth = hits_scores(G)

    write_report(args.out, ranked)
    print(f"Wrote markdown report to {args.out}/report.md")

if __name__ == "__main__":
    main()
