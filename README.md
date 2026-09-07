# Classification and Comparative Analysis of Modern Methods in Optimizing Distributed Database Performance

**PilotDB vs. FAAQP on a Citus-based Distributed Cluster**

Undergraduate thesis project — experimental comparison of two Approximate Query
Processing (AQP) systems, PilotDB (online sampling with a priori error
guarantees) and FAAQP (offline statistical modeling via Bitmap-augmented
Sum-Product Networks), evaluated on a real distributed PostgreSQL/Citus
cluster using the Star Schema Benchmark (SSB, SF1).

**Author:** Hamed Sabour Yaraghi
**Advisor:** Dr. Maryam Ramezani

## Overview

This repository contains the infrastructure, configuration, patches, query
sets, and analysis scripts used to run a controlled experimental comparison
between PilotDB and FAAQP on identical data and identical SQL queries. It
does **not** vendor the source code of PilotDB or FAAQP themselves — both are
cloned from their own public repositories (linked below) and patched locally;
only the patches and our own artifacts are committed here.

### Systems under test

- **[PilotDB](https://github.com/uiuc-kang-lab/PilotDB)** — database-agnostic
  online AQP middleware with a priori error guarantees (SIGMOD 2025).
- **[FAAQP](https://github.com/DogeWang/FAAQP)** — offline AQP based on
  Bitmap-augmented Sum-Product Networks (BSPN), extending DeepDB/RSPN.

### Infrastructure

- 3-node **Citus** cluster (1 coordinator + 2 workers) via Docker Compose,
  with persistent named volumes.
- **Star Schema Benchmark (SSB)**, scale factor 1 (~6,001,215 rows in
  `lineorder`), generated with
  [ssb-dbgen](https://github.com/vadimtk/ssb-dbgen).

## Repository structure

```
infra/            Docker Compose file for the Citus cluster
data/             Schema DDL + instructions for generating SSB data
pilotdb/          Config templates, patches, and query files for PilotDB
faaqp/            Patches and query files for FAAQP
experiments/      Scripts to run the experiment sweep + aggregate results
charts/           Generated result charts (PNG)
```

## Reproducing the environment

### 1. Clone the upstream systems (not included here)

```bash
git clone https://github.com/uiuc-kang-lab/PilotDB.git
git clone https://github.com/DogeWang/FAAQP.git
git clone https://github.com/vadimtk/ssb-dbgen.git
```

### 2. Apply the patches in this repo

```bash
cd PilotDB && git apply ../pilotdb/patches/pilotdb_server.patch
cd ../FAAQP && git apply ../faaqp/patches/physical_db.patch
```

### 3. Bring up the Citus cluster

```bash
cd infra
docker compose up -d
docker exec -it coordinator psql -U postgres -c "SELECT citus_add_node('worker1', 5432);"
docker exec -it coordinator psql -U postgres -c "SELECT citus_add_node('worker2', 5432);"
docker exec -it coordinator psql -U postgres -d postgres \
  -c "INSERT INTO pg_dist_authinfo (nodeid, rolename, authinfo) VALUES (0, 'postgres', 'password=postgres');"
```

### 4. Generate and load SSB data (SF1)

```bash
cd ssb-dbgen && make
./dbgen -s 1 -T c && ./dbgen -s 1 -T l && ./dbgen -s 1 -T p && ./dbgen -s 1 -T s && ./dbgen -s 1 -T d

psql -h localhost -U postgres -d postgres -f ../data/ssb_schema.sql
# load each table via \COPY — see data/README.md for the full loading steps
```

### 5. Configure PilotDB

```bash
cp pilotdb/db_configs/citus.yml.example PilotDB/db_configs/citus.yml
# edit citus.yml with your actual host/password
```

### 6. Run the experiment sweep

```bash
cd experiments
./run_pilotdb_sweep.sh
python3 aggregate_sweep.py
```

## Results summary

| Query | Selectivity | FAAQP latency | FAAQP error | PilotDB best latency | PilotDB error | Guarantee held |
|---|---|---|---|---|---|---|
| Q1 | ~2.0% | 0.340s | 0.42% | 0.185s | 0.47% | Yes (0/15) |
| Q2 | ~0.07% | 0.045s | 1.84% | ~0.41s | 0.00% | Yes (0/15) |
| Q3 | ~0.41% | 0.030s | 0.13% | 0.181s | 1.65% | Yes (0/15) |

See `charts/` for the full latency-vs-threshold and error-vs-threshold sweep
results, and `experiments/results/` for the raw CSV data.

**Key finding:** neither system is universally superior. FAAQP offers
consistent low latency regardless of query selectivity but no formal
statistical guarantee. PilotDB offers a validated a priori error guarantee
(never violated across 225 runs) and real speedups for moderately selective
queries, but its sampling mechanism fails to engage reliably for highly
selective predicates, degrading to full-scan performance.

## Citation

If referencing this work, please cite the original systems:

```
Zhu, Y., Jin, T., Baziotis, S., Zhang, C., Mendis, C., & Kang, D. (2025).
PilotDB: Database-Agnostic Online Approximate Query Processing with A Priori
Error Guarantees. Proc. ACM Manag. Data, 3(3), Article 198.

Wang, D. FAAQP: Fast and Accurate Approximate Query Processing based on
Bitmap-augmented Sum-Product Network. github.com/DogeWang/FAAQP
```
