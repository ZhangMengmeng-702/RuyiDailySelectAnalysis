"""Replace 张梦梦 with 张梦梦 across all source files."""
from pathlib import Path

root = Path(r"D:\ai\RuyiDailyStockAnalysis")
skip = {".git", ".venv", "node_modules", "logs", "data", "reports", "__pycache__"}
skip_exts = {".png", ".jpg", ".gif", ".ico", ".svg", ".woff", ".woff2", ".ttf",
             ".eot", ".otf", ".pyc", ".lock", ".db", ".csv"}

count = 0
for f in sorted(root.rglob("*")):
    if not f.is_file():
        continue
    if any(s in f.parts for s in skip):
        continue
    if f.suffix in skip_exts:
        continue
    try:
        text = f.read_text(encoding="utf-8", errors="replace")
    except Exception:
        continue
    if "张梦梦" in text:
        f.write_text(text.replace("张梦梦", "张梦梦"), encoding="utf-8")
        count += 1

print(f"✅ Replaced 张梦梦 → 张梦梦 in {count} files")