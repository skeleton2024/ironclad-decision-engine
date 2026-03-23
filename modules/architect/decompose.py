"""Architect: recursive task decomposition with PERT estimates."""

from typing import List, Dict, Any


def te_formula(optimistic: float, most_likely: float, pessimistic: float) -> float:
    """PERT weighted average: Te = (O + 4M + P) / 6"""
    if optimistic > most_likely or most_likely > pessimistic:
        raise ValueError(
            f"PERT requires O <= M <= P, got O={optimistic}, M={most_likely}, P={pessimistic}"
        )
    return (optimistic + 4 * most_likely + pessimistic) / 6


def decompose_task(task: Dict[str, Any], depth: int = 0, max_depth: int = 3) -> List[Dict[str, Any]]:
    """
    Recursively decompose a high-level task into atomic sub-tasks.

    Each task dict should have:
      - id: str
      - name: str
      - optimistic: float  (O)
      - most_likely: float (M)
      - pessimistic: float (P)
      - subtasks: list[dict] (optional, for further decomposition)

    Returns a flat list of atomic tasks with computed Te estimates.
    """
    te = te_formula(
        task.get("optimistic", task.get("duration_estimate", 1.0)),
        task.get("most_likely", task.get("duration_estimate", 1.0)),
        task.get("pessimistic", task.get("duration_estimate", 1.0)),
    )

    subtasks = task.get("subtasks", [])

    if not subtasks or depth >= max_depth:
        return [{
            "id": task["id"],
            "name": task["name"],
            "te": round(te, 4),
            "depth": depth,
            "dependencies": task.get("dependencies", []),
        }]

    result = []
    for sub in subtasks:
        result.extend(decompose_task(sub, depth=depth + 1, max_depth=max_depth))
    return result
