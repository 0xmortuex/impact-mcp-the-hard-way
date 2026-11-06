"""Run every module's main.py for real, the way CI does.

Each main.py checks its own results with assert (exact edges, cycles, impact text, and in
module 07 a real MCP session over stdio), so a chapter whose code drifts from what its
README claims fails here.

Usage: python verify.py            # all modules
       python verify.py 03 05      # just these
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    wanted = set(sys.argv[1:])
    modules = sorted(p for p in ROOT.iterdir() if p.is_dir() and p.name[:2].isdigit())
    if wanted:
        modules = [m for m in modules if m.name[:2] in wanted]
    if not modules:
        print("no modules selected")
        return 2
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    failed = []
    for m in modules:
        num = m.name[:2]
        proc = subprocess.run(
            [sys.executable, str(m / "main.py")], capture_output=True, text=True, encoding="utf-8", env=env, timeout=300
        )
        ok = proc.returncode == 0 and f"module {num} OK" in proc.stdout
        print(f"{'PASS' if ok else 'FAIL'}  {m.name}")
        if not ok:
            failed.append(m.name)
            print(proc.stdout[-1500:])
            print(proc.stderr[-1500:])
    print(f"\n{len(modules) - len(failed)}/{len(modules)} modules verified")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
