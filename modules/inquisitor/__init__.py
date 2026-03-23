"""Inquisitor: adversarial red-team auditor for plans."""

from typing import List, Dict, Any


class Inquisitor:
    """
    Challenges a plan by identifying failure modes,
    missing dependencies, and unrealistic estimates.
    """

    # Default risk thresholds
    HIGH_TE_THRESHOLD = 20.0  # days — flag tasks with Te above this
    MAX_DEPENDENCY_DEPTH = 5

    def audit(self, atomic_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run adversarial audit on a list of atomic tasks.

        Returns a report with:
          - flags: list of issues found
          - risk_score: 0.0 (safe) to 1.0 (critical)
          - passed: bool
        """
        flags: List[str] = []
        task_ids = {t["id"] for t in atomic_tasks}

        for t in atomic_tasks:
            # Flag high-duration tasks
            if t.get("te", 0) > self.HIGH_TE_THRESHOLD:
                flags.append(f"HIGH_DURATION: Task '{t['name']}' (id={t['id']}) has Te={t['te']:.2f} > {self.HIGH_TE_THRESHOLD}")

            # Flag missing dependency references
            for dep in t.get("dependencies", []):
                if dep not in task_ids:
                    flags.append(f"MISSING_DEP: Task '{t['name']}' depends on unknown task '{dep}'")

            # Flag deep nesting
            if t.get("depth", 0) >= self.MAX_DEPENDENCY_DEPTH:
                flags.append(f"DEEP_NESTING: Task '{t['name']}' at depth {t['depth']}")

        risk_score = min(1.0, len(flags) / max(len(atomic_tasks), 1))

        return {
            "flags": flags,
            "risk_score": round(risk_score, 4),
            "passed": len(flags) == 0,
            "total_tasks_audited": len(atomic_tasks),
        }
