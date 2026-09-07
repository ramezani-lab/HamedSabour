import json, csv, glob, pickle
import statistics as stats

BASE = "/home/ubuntu/paper-experiment"

with open(f"{BASE}/ground_truth.pkl", "rb") as f:
    ground_truth = pickle.load(f)


def get_ground_truth_value(query_idx):
    return ground_truth[query_idx][0][0]


def extract_value(result_dict):
    """Pull the single scalar value regardless of the aggregate column's label
    (e.g. 'revenue' vs '?column?' depending on whether the query used an alias)."""
    inner = list(result_dict.values())[0]
    return list(inner.values())[0]


def parse_pilotdb_log(path):
    results = []
    with open(path) as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        if lines[i].strip() == "{":
            block = []
            depth = 0
            while i < len(lines):
                line = lines[i]
                block.append(line)
                depth += line.count("{")
                depth -= line.count("}")
                i += 1
                if depth == 0:
                    break
            try:
                obj = json.loads("".join(block))
                results.append(obj)
            except json.JSONDecodeError:
                pass
        else:
            i += 1
    return results


rows = []

for q in [1, 2, 3]:
    gt_value = get_ground_truth_value(q - 1)

    for path in sorted(glob.glob(f"{BASE}/pilotdb-sweep/q{q}_err*.jsonl")):
        err_label = path.split("_err")[1].replace(".jsonl", "")
        records = parse_pilotdb_log(path)

        latencies, values = [], []
        for d in records:
            if d.get("status") == "success":
                latencies.append(d["runtime"])
                values.append(extract_value(d["result"]))

        if not latencies:
            print(f"WARNING: no successful runs parsed from {path}")
            continue

        errors = [abs(v - gt_value) / gt_value for v in values]

        rows.append({
            "query": f"Q{q}",
            "error_threshold": err_label,
            "n_runs": len(latencies),
            "median_latency_s": round(stats.median(latencies), 4),
            "stdev_latency_s": round(stats.stdev(latencies), 4) if len(latencies) > 1 else 0.0,
            "median_observed_error_pct": round(stats.median(errors) * 100, 4),
            "max_observed_error_pct": round(max(errors) * 100, 4),
            "fraction_exceeding_declared_bound": round(
                sum(1 for e in errors if e > float(err_label)) / len(errors), 4
            ),
        })

out_path = f"{BASE}/sweep_results.csv"
fieldnames = ["query", "error_threshold", "n_runs", "median_latency_s", "stdev_latency_s",
              "median_observed_error_pct", "max_observed_error_pct", "fraction_exceeding_declared_bound"]

with open(out_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

print(f"Saved {len(rows)} rows to {out_path}\n")
for r in rows:
    print(r)
