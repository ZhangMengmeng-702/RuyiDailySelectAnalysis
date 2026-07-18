#!/usr/bin/env python3
"""Scan project for old brand references."""
from pathlib import Path

root = Path(r"D:\ai\RuyiDailyStockAnalysis")
skip_dirs = {".git", ".venv", "node_modules", "logs", "data", "reports", "__pycache__",
             "dist", "build", ".agents", ".claude", ".github", "assets",
             ".mypy_cache", ".pytest_cache", "cache", "strategies"}
skip_ext = {".png", ".jpg", ".gif", ".ico", ".svg", ".woff", ".ttf", ".pyc",
            ".lock", ".csv", ".yaml", ".yml", ".db"}

old_brands = ["RuyiDailyStockAnalysis", "RuyiDailyStockAnalysis",
              "如意金股", "如意金股",
              "金股分析系统", "智能分析系统", "ruyi-web", "ruyi-desktop",
              "ruyi_web", "ruyi_desktop"]

results = []
for f in sorted(root.rglob("*")):
    if not f.is_file(): continue
    if any(s in f.parts for s in skip_dirs): continue
    if f.suffix in skip_ext: continue
    try:
        text = f.read_text(encoding="utf-8", errors="replace")
    except:
        continue
    for brand in old_brands:
        if brand in text:
            results.append((f.relative_to(root), brand))
            break

print(f"Found {len(results)} files with old brand references:\n")
for path, brand in sorted(results, key=lambda x: str(x[0])):
    print(f"  {path} → '{brand}'")