"""Shared calculation pipeline; durations are hours of serial effort."""
from importlib import import_module
from modules.architect.decompose import decompose_task
from modules.inquisitor import Inquisitor

def analyze_plan(goal, plan=None, max_depth=3):
    demo = plan is None
    if demo:
        plan = {"id": "demo", "name": goal, "subtasks": [
            {"id": "scope", "name": "示例：整理问题", "optimistic": 1, "most_likely": 2, "pessimistic": 4},
            {"id": "compare", "name": "示例：比较方案", "optimistic": 2, "most_likely": 4, "pessimistic": 8, "dependencies": ["scope"]},
            {"id": "review", "name": "示例：复核假设", "optimistic": 1, "most_likely": 2, "pessimistic": 5, "dependencies": ["compare"]},
        ]}
    atoms = decompose_task(plan, max_depth=max_depth)
    ids = [a['id'] for a in atoms]
    if len(ids) != len(set(ids)):
        raise ValueError("Task IDs must be unique")
    audit = Inquisitor().audit(atoms)
    mc = import_module('shared.quant-engine.sim').monte_carlo_simulate(atoms, seed=42)
    return {
        "atomic_tasks": [{"task_id": a['id'], "description": a['name'], "estimated_hours": a['te'],
                          "dependencies": a['dependencies'], "risk_level": "medium"} for a in atoms],
        "monte_carlo": {**{f'{k}_hours': mc[k] for k in ['mean','min','max','p10','p50','p90']}, "simulation_count": mc['iterations']},
        "risks": [{"risk_id": f'R{i+1}', "description": flag, "severity": "high", "mitigation": "复核任务和依赖"}
                  for i, flag in enumerate(audit['flags'])],
        "recommended_decision": ("示例计划：" if demo else "计划检查：") + ("请先复核风险项" if audit['flags'] else "规则检查通过，可继续评估资源与优先级"),
        "reasoning": f"{'内置示例估时' if demo else '用户提供估时'}；{len(atoms)} 个任务。三角分布模拟串行总工时，P90={mc['p90']:.2f} 小时。",
    }
