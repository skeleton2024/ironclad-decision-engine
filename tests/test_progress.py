#!/usr/bin/env python3
"""
Progress test: exercises Architect decomposition, Inquisitor audit,
and Monte Carlo simulation end-to-end. Run with:
    PYTHONPATH=. python3 tests/test_progress.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.schemas.atomic_task_py import AtomicTask
from modules.architect.decompose import te_formula, decompose_task
from modules.inquisitor import Inquisitor

# quant-engine has a hyphen — need importlib
import importlib
sim = importlib.import_module("shared.quant-engine.sim")

PASS = 0
FAIL = 0

def check(label, condition):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✓ {label}")
    else:
        FAIL += 1
        print(f"  ✗ {label}")

# ─── 1. AtomicTask schema ───
print("\n[1] AtomicTask schema")
t = AtomicTask(id="t1", name="Design API", duration_estimate=3.0, dependencies=[])
check("AtomicTask instantiation", t.id == "t1" and t.duration_estimate == 3.0)
check("AtomicTask to_dict", t.to_dict()["name"] == "Design API")

# ─── 2. PERT Te formula ───
print("\n[2] PERT Te formula")
te = te_formula(1.0, 3.0, 5.0)
check(f"Te(1,3,5) = {te:.4f} (expect 3.0)", abs(te - 3.0) < 0.001)
te2 = te_formula(2.0, 4.0, 12.0)
expected = (2 + 16 + 12) / 6  # 5.0
check(f"Te(2,4,12) = {te2:.4f} (expect {expected:.4f})", abs(te2 - expected) < 0.001)

# ─── 3. Architect decompose ───
print("\n[3] Architect decomposition")
plan = {
    "id": "root",
    "name": "Build MVP",
    "optimistic": 10, "most_likely": 15, "pessimistic": 30,
    "subtasks": [
        {"id": "s1", "name": "Backend", "optimistic": 3, "most_likely": 5, "pessimistic": 10, "dependencies": []},
        {"id": "s2", "name": "Frontend", "optimistic": 4, "most_likely": 7, "pessimistic": 14, "dependencies": ["s1"]},
        {"id": "s3", "name": "Testing", "optimistic": 2, "most_likely": 3, "pessimistic": 8, "dependencies": ["s1", "s2"]},
    ],
}
atoms = decompose_task(plan)
check(f"Decomposed into {len(atoms)} atomic tasks (expect 3)", len(atoms) == 3)
check("All atoms have Te values", all("te" in a for a in atoms))

# ─── 4. Inquisitor audit ───
print("\n[4] Inquisitor audit")
inq = Inquisitor()
report = inq.audit(atoms)
check(f"Audit passed (no flags expected): passed={report['passed']}", report["passed"])
check(f"Risk score = {report['risk_score']}", report["risk_score"] == 0.0)

# inject a bad task to test flagging
bad_atoms = atoms + [{"id": "s4", "name": "Impossible", "te": 999.0, "dependencies": ["missing_dep"], "depth": 0}]
bad_report = inq.audit(bad_atoms)
check(f"Bad audit flagged issues: {len(bad_report['flags'])} flags", len(bad_report["flags"]) >= 2)
check(f"Bad audit failed: passed={bad_report['passed']}", not bad_report["passed"])

# ─── 5. Monte Carlo simulation ───
print("\n[5] Monte Carlo simulation")
mc_tasks = [
    {"optimistic": 3, "most_likely": 5, "pessimistic": 10},
    {"optimistic": 4, "most_likely": 7, "pessimistic": 14},
    {"optimistic": 2, "most_likely": 3, "pessimistic": 8},
]
result = sim.monte_carlo_simulate(mc_tasks, iterations=5000, seed=42, success_threshold=20.0)
check(f"MC mean = {result['mean']:.2f} (sanity: 10-25)", 10 < result["mean"] < 25)
check(f"MC p90 = {result['p90']:.2f} > p10 = {result['p10']:.2f}", result["p90"] > result["p10"])
check(f"Success probability @ 20d = {result.get('success_probability', 'N/A')}", result.get("success_probability") is not None)

# ─── Summary ───
print(f"\n{'='*40}")
print(f"PASSED: {PASS}  |  FAILED: {FAIL}")
if FAIL:
    print("⚠️  Some checks failed!")
    sys.exit(1)
else:
    print("✅ All checks passed!")
    sys.exit(0)
