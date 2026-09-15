#!/usr/bin/env python3
"""Check the recorded LambdaVM experiment, not rerun the prover benchmark.

Recomputes production paired mean timings from the supplied TSV rows; reported
bootstrap intervals remain measurement evidence, not newly generated intervals.
"""
import csv
from decimal import Decimal as D
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "experiments" / "lambdavm-anchors"


def rows(name):
    with (DATA / name).open(newline="") as source:
        return list(csv.DictReader(source, delimiter="\t"))


def paired_mean(name, expected_rounds):
    records = rows(name)
    rounds = {}
    for row in records:
        group = rounds.setdefault(int(row["round"]), {})
        assert row["cell"] not in group
        group[row["cell"]] = row
    assert len(rounds) == expected_rounds
    differences = []
    for group in rounds.values():
        assert set(group) == {"control", "anchor_only", "query_only", "actual"}
        differences.append(
            D(group["actual"]["internal_seconds"])
            - D(group["control"]["internal_seconds"]))
    return sum(differences) / D(len(differences)) * 1000


def check():
    data = json.loads((DATA / "measurement.json").read_text())
    assert data["cpu_trace_rows"] == 32768 and data["subproof_count"] == 26
    assert (data["cpu_queries_control"], data["cpu_queries_actual"],
            data["non_cpu_queries"]) == (219, 208, 219)
    assert (data["anchor_count"], data["anchor_width"],
            data["grinding_bits"]) == (2, 38, 20)
    queries_removed = data["cpu_queries_control"] - data["cpu_queries_actual"]
    removed = queries_removed * data["serialized_query_bytes"]
    saving = data["control_bytes"] - data["actual_bytes"]
    assert removed == 61688
    assert saving == removed - data["serialized_anchor_bytes"] == 59832
    assert saving == data["measured_saving_bytes"]
    assert (data["cpu_control_bytes"], data["cpu_actual_bytes"]) == (1233024, 1173192)
    assert data["cpu_control_bytes"] - data["cpu_actual_bytes"] == saving
    cpu = json.loads((DATA / "cpu-size-breakdown.json").read_text())
    for arm, size in (("control", data["cpu_control_bytes"]),
                      ("experimental", data["cpu_actual_bytes"])):
        assert cpu[f"{arm}_cpu_standalone_bytes"] == size
        assert cpu[f"{arm}_empty_vm_bytes"] == 176
        assert (cpu[f"{arm}_cpu_only_vm_bytes"] - cpu[f"{arm}_empty_vm_bytes"]
                == cpu[f"{arm}_cpu_marginal_bytes"] == size)
    assert cpu["cpu_standalone_savings"] == cpu["net_savings"] == saving

    cell_bytes = {"control": 36868888, "anchor_only": 36870744,
                  "query_only": 36807200, "actual": 36809056}
    for row in rows("process-prove-runs.tsv"):
        assert int(row["proof_bytes"]) == cell_bytes[row["cell"]]
    prove_ms = paired_mean("process-prove-runs.tsv", 20)
    verify_ms = paired_mean("process-verify-runs.tsv", 50)
    assert abs(prove_ms - D("-15.2")) < D("0.1")
    assert abs(verify_ms - D("0.02")) < D("0.01")
    summary = rows("benchmark-summary.tsv")
    for surface, low, high in (("prove", "-49.4", "18.9"),
                               ("verify", "-0.62", "0.52")):
        record = next(row for row in summary if row["surface"] == surface
                      and row["metric"] == "CLI internal wall time"
                      and "grinding=0" not in row["notes"])
        assert D(record["ci95_low"]) == D(low) < 0
        assert D(record["ci95_high"]) == D(high) > 0

    return {"status": "PASS", "scope": "recorded CPU subproof and complete benchmark proof",
            "measured_serialized_saving_bytes": saving,
            "cpu_subproof_percent_saved":
                str(D(saving) * 100 / D(data["cpu_control_bytes"])),
            "complete_proof_percent_saved":
                str(D(saving) * 100 / D(data["control_bytes"])),
            "paired_prove_change_ms": str(prove_ms),
            "paired_verify_change_ms": str(verify_ms),
            "benchmark_rerun": False,
            "bootstrap_intervals_recomputed": False}


if __name__ == "__main__":
    print(json.dumps(check(), indent=2))
