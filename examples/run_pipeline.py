import argparse, os
from fraudgraph.etl import load_transactions, build_graph
from fraudgraph.algorithms import louvain_communities, hits_scores, rank_communities_by_suspicion
from fraudgraph.ml_model import rank_with_ml


def write_report(out_dir, ranked_ml):
    os.makedirs(out_dir, exist_ok=True)
    md_path = os.path.join(out_dir, "report.md")
    with open(md_path, "w") as f:
        f.write("# FraudGraph Report\n\n")
        for i, (heuristic_score, nodes, ml_prob) in enumerate(ranked_ml[:10], 1):
            acc = [n for n in nodes if str(n).startswith("account:")]
            dev = [n for n in nodes if str(n).startswith("device:")]
            ip = [n for n in nodes if str(n).startswith("ip:")]
            instr = [n for n in nodes if str(n).startswith("instrument:")]

            f.write(
                f"## Community {i} — ML Fraud Prob: {ml_prob:.3f}, Heuristic: {heuristic_score:.3f}\n"
            )
            f.write(
                f"- Accounts: {len(acc)}, Devices: {len(dev)}, IPs: {len(ip)}, Instruments: {len(instr)}\n\n"
            )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--transactions", required=True)
    ap.add_argument("--out", default="reports")
    args = ap.parse_args()

    print("🚀 Loading transactions...")
    df = load_transactions(args.transactions)

    print("🔗 Building graph...")
    G = build_graph(df, include_id_links=True)

    print("🧩 Running Louvain + heuristic scoring...")
    comms = louvain_communities(G)
    ranked = rank_communities_by_suspicion(G, comms)

    print("🤖 Training ML model for fraud probability scoring...")
    ranked_ml = rank_with_ml(G, ranked)

    print("📝 Writing report...")
    write_report(args.out, ranked_ml)
    print(f"✅ Report written to {args.out}/report.md")


if __name__ == "__main__":
    main()
