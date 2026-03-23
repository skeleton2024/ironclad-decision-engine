"""Quant Engine: Monte Carlo simulation for project risk estimation."""

import random
from typing import List, Dict, Any, Optional


def monte_carlo_simulate(
    atomic_tasks: List[Dict[str, Any]],
    iterations: int = 1000,
    seed: Optional[int] = None,
    success_threshold: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Run Monte Carlo simulation over a set of atomic tasks.

    For each iteration, samples a duration for each task from a
    triangular distribution (optimistic, most_likely, pessimistic)
    and sums total project duration.

    Args:
        atomic_tasks: list of task dicts with 'optimistic', 'most_likely', 'pessimistic' keys
                      (falls back to 'te' if PERT values not present)
        iterations: number of simulation runs
        seed: optional random seed for reproducibility
        success_threshold: if set, calculates probability of finishing within this duration

    Returns:
        dict with mean, p10, p50, p90, min, max durations, and optional success_probability
    """
    if seed is not None:
        random.seed(seed)

    durations = []

    for _ in range(iterations):
        total = 0.0
        for task in atomic_tasks:
            o = task.get("optimistic", task.get("te", 1.0))
            m = task.get("most_likely", task.get("te", 1.0))
            p = task.get("pessimistic", task.get("te", 1.0))
            # Triangular distribution: good proxy for PERT
            sampled = random.triangular(o, p, m)
            total += sampled
        durations.append(total)

    durations.sort()
    n = len(durations)

    result = {
        "iterations": iterations,
        "mean": round(sum(durations) / n, 4),
        "min": round(durations[0], 4),
        "max": round(durations[-1], 4),
        "p10": round(durations[int(n * 0.1)], 4),
        "p50": round(durations[int(n * 0.5)], 4),
        "p90": round(durations[int(n * 0.9)], 4),
    }

    if success_threshold is not None:
        successes = sum(1 for d in durations if d <= success_threshold)
        result["success_probability"] = round(successes / n, 4)
        result["success_threshold"] = success_threshold

    return result
