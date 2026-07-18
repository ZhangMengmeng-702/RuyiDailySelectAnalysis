#!/usr/bin/env python3
"""Build frontend after branding changes."""
import subprocess
from pathlib import Path

root = Path(r"D:\ai\RuyiDailyStockAnalysis")
npm = r"C:\Program Files\nodejs\npm.CMD"

print("Building frontend...")
r = subprocess.run(
    [npm, "run", "build"],
    cwd=str(root / "apps" / "dsa-web"),
    capture_output=True, text=True, timeout=300
)
if r.returncode == 0:
    for line in r.stdout.splitlines():
        if "built in" in line.lower() or "✓" in line or "error" in line.lower():
            print(f"  {line}")
    print(f"\n✅ Frontend build succeeded!")
else:
    print(f"❌ BUILD FAILED (exit {r.returncode})")
    print(r.stderr[-800:])