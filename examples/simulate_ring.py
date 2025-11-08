import argparse, random, csv, time
random.seed(0)

def generate(n_accounts=300, ring_size=15, benign_edges=1200, ring_edges=250):
    ts = int(time.time())
    accounts = [f"a{i}" for i in range(n_accounts)]
    ring = random.sample(accounts, ring_size)
    devices = [f"d{i}" for i in range(max(50, ring_size//2))]
    ips = [f"10.0.0.{i}" for i in range(1, max(50, ring_size//2)+1)]
    instruments = [f"card{i}" for i in range(max(60, ring_size))]

    rows = []
    # benign background
    for _ in range(benign_edges):
        s, r = random.sample(accounts, 2)
        amt = round(random.uniform(5, 150), 2)
        rows.append([ts, s, r, amt, "", "", ""])

    # collusive ring: dense & shared identifiers
    for _ in range(ring_edges):
        s, r = random.sample(ring, 2)
        amt = round(random.uniform(20, 80), 2)
        dev = random.choice(devices)
        ip = random.choice(ips)
        instr = random.choice(instruments)
        rows.append([ts, s, r, amt, dev, ip, instr])
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/sim_transactions.csv")
    args = ap.parse_args()
    rows = generate()
    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["timestamp","sender","receiver","amount","device_id","ip","instrument_id"])
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {args.out}")

if __name__ == "__main__":
    main()
