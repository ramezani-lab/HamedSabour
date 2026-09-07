import json, csv, glob, pickle
import statistics as stats

BASE = "/home/ubuntu/paper-experiment"

# --- Load ground truth ---
with open(f"{BASE}/ground_truth.pkl", "rb") as f:
    ground_truth = pickle.load(f)
print("Ground truth loaded:", ground_truth)

# Confirmed structure: {0: [(446031203850,)], 1: [(...,)], 2: [(...,)]}
def get_ground_truth_value(query_idx):
    return ground_truth[query_idx][0][0]


def extract_value(result_dict):
    """Pull the single scalar value out of a PilotDB-style {'colname': {'0': value}} result."""
    inner = list(result_dict.values())[0]
    return list(inner.values())[0]


def parse_pilotdb_log(path):
    """
    pilotdb_client.py prints two things per invocation:
      1) print(payload)               -> a Python dict repr, NOT valid JSON (single quotes),
                                          always on one line
      2) print(json.dumps(result, indent=2)) -> pretty-printed JSON across multiple lines

    We detect the start of a JSON block as a line that is exactly '{' (the payload line
    never qualifies, since it has other content before/after its braces on the same line).
    Once inside a block, we track depth by counting '{' and '}' characters anywhere in
    each line (not just whole-line matches), since nested keys like '"result": {' have
    the opening brace preceded by other text.
    """
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

# --- PilotDB ---
for q in [1, 2, 3]:
    gt_value = get_ground_truth_value(q - 1)

    for mode in ["exact", "aqp"]:
        path = f"{BASE}/pilotdb-results/q{q}_{mode}.jsonl"
        try:
            records = parse_pilotdb_log(path)
        except FileNotFoundError:
            print(f"WARNING: missing {path}")
            continue

        latencies, values = [], []
        for d in records:
            if d.get("status") == "success":
                latencies.append(d["runtime"])
                values.append(extract_value(d["result"]))

        if not latencies:
            print(f"WARNING: no successful runs parsed from {path} (found {len(records)} JSON blocks)")
            continue

        row = {
            "system": f"PilotDB-{mode}",
            "query": f"Q{q}",
            "n_runs": len(latencies),
            "median_latency_s": round(stats.median(latencies), 4),
            "stdev_latency_s": round(stats.stdev(latencies), 4) if len(latencies) > 1 else 0.0,
            "median_result": stats.median(values),
        }

        if mode == "aqp" and gt_value:
            errors = [abs(v - gt_value) / gt_value for v in values]
            row["median_relative_error_pct"] = round(stats.median(errors) * 100, 4)
            row["max_relative_error_pct"] = round(max(errors) * 100, 4)
            row["fraction_exceeding_5pct_bound"] = round(
                sum(1 for e in errors if e > 0.05) / len(errors), 4
            )

        rows.append(row)

# --- FAAQP ---
faaqp_latencies = {1: [], 2: [], 3: []}
faaqp_errors = {1: None, 2: None, 3: None}

for path in sorted(glob.glob(f"{BASE}/faaqp-results/run_*.csv")):
    with open(path) as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            if i > 3:
                break
            faaqp_latencies[i].append(float(row["latency"]))
            faaqp_errors[i] = float(row["average_relative_error"]) * 100  # to percent

for q in [1, 2, 3]:
    lat = faaqp_latencies[q]
    if not lat:
        print(f"WARNING: no FAAQP results found for Q{q}")
        continue
    rows.append({
        "system": "FAAQP",
        "query": f"Q{q}",
        "n_runs": len(lat),
        "median_latency_s": round(stats.median(lat), 4),
        "stdev_latency_s": round(stats.stdev(lat), 4) if len(lat) > 1 else 0.0,
        "median_result": None,
        "median_relative_error_pct": round(faaqp_errors[q], 4) if faaqp_errors[q] is not None else None,
        "max_relative_error_pct": None,
        "fraction_exceeding_5pct_bound": None,
    })

# --- Write output ---
fieldnames = [
    "system", "query", "n_runs", "median_latency_s", "stdev_latency_s",
    "median_result", "median_relative_error_pct", "max_relative_error_pct",
    "fraction_exceeding_5pct_bound",
]

out_path = f"{BASE}/final_comparison.csv"
with open(out_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        for k in fieldnames:
            r.setdefault(k, None)
        writer.writerow(r)

print(f"\nSaved {len(rows)} rows to {out_path}\n")
for r in rows:
    print(r)
