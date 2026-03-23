#!/usr/bin/env python3
"""Ironclad heartbeat runner.

Non-destructive: reads repo files and updates ONLY ebrain skill/heartbeat_state.json.
Prints a concise progress report suitable for sending.

Usage:
  python3 heartbeat_once.py
Exit codes:
  0 -> no report needed (interval not reached)
  2 -> report generated (interval reached)
"""

from __future__ import annotations

import datetime as _dt
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
STATE_PATH = ROOT / "heartbeat_state.json"


def _utcnow() -> _dt.datetime:
    return _dt.datetime.now(tz=_dt.timezone.utc)


def _parse_utc(s: str) -> _dt.datetime:
    # Accept ISO8601 with 'Z'
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return _dt.datetime.fromisoformat(s)


def _iso_z(dt: _dt.datetime) -> str:
    return dt.astimezone(_dt.timezone.utc).isoformat().replace("+00:00", "Z")


def _load_state() -> dict:
    if not STATE_PATH.exists():
        return {"last_report_utc": "1970-01-01T00:00:00Z", "report_interval_hours": 10}
    with STATE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_state(state: dict) -> None:
    tmp = STATE_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, STATE_PATH)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _file_exists(rel: str) -> bool:
    return (ROOT / rel).exists()


def _run_tests_smoke() -> tuple[bool, str]:
    # Non-destructive smoke test: try running pure-python test_basic.py as a script.
    test_path = ROOT / "tests" / "test_basic.py"
    if not test_path.exists():
        return False, "tests/test_basic.py missing"

    # Run in-process to avoid shell quoting problems.
    # Ensure repo root on sys.path.
    sys.path.insert(0, str(ROOT))
    try:
        ns = {"__name__": "__main__"}
        code = test_path.read_text(encoding="utf-8")
        exec(compile(code, str(test_path), "exec"), ns, ns)
        return True, "test_basic.py OK"
    except Exception as e:
        return False, f"test_basic.py FAIL: {e}"


def build_report() -> str:
    lines: list[str] = []
    lines.append("[项目记忆] Ironclad-Decision-Engine 进度心跳")

    # Quick file presence checks
    checks = {
        "PRD": _file_exists("prd.md"),
        "AtomicTask(pure)": _file_exists("core/schemas/atomic_task_py.py"),
        "Architect": _file_exists("modules/architect/decompose.py"),
        "Inquisitor": _file_exists("modules/inquisitor/__init__.py"),
        "QuantEngine": _file_exists("shared/quant-engine/sim.py"),
        "Tests": _file_exists("tests/test_basic.py"),
    }
    ok = [k for k, v in checks.items() if v]
    missing = [k for k, v in checks.items() if not v]

    lines.append(f"- 关键文件：OK={len(ok)}/{len(checks)}" + ("" if not missing else f"；缺失：{', '.join(missing)}"))

    # Smoke test
    passed, msg = _run_tests_smoke()
    lines.append(f"- 自检：{msg}")

    # Tiny TODO hint: detect if FastAPI entry exists
    if not _file_exists("main.py"):
        lines.append("- 下一步：补齐 FastAPI main.py + 核心 API endpoints（PRD M5 相关）")

    return "\n".join(lines)


def main() -> int:
    state = _load_state()
    interval_h = float(state.get("report_interval_hours", 10))

    now = _utcnow()
    last = _parse_utc(state.get("last_report_utc", "1970-01-01T00:00:00Z"))
    elapsed_h = (now - last).total_seconds() / 3600.0

    if elapsed_h < interval_h:
        # No report needed
        return 0

    report = build_report()
    print(report)

    # Update state timestamp only (non-destructive)
    state["last_report_utc"] = _iso_z(now)
    state["report_interval_hours"] = int(interval_h)
    _save_state(state)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
