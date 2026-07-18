#!/usr/bin/env python3
"""品牌化改造：统一替换展示层品牌与说明信息。
只改用户可见品牌文字，不改API路径、数据库字段、依赖、密钥。
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ========= 品牌映射 =========
# 规则：key=旧品牌/名称, value=新品牌/名称
# 按最长匹配优先排序，避免短字符串错误替换
REPLACEMENTS = [
    # 中文品牌
    ("如意金股", "如意金股"),
    ("如意金股", "如意金股"),
    ("如意金股", "如意金股"),
    ("如意金股", "如意金股"),
    ("如意金股", "如意金股"),
    ("如意金股", "如意金股"),
    ("金股分析系统", "金股分析系统"),
    
    # 英文品牌（展示用）
    ("RuyiDailyStockAnalysis", "RuyiDailyStockAnalysis"),
    ("RuyiDailyStockAnalysis", "RuyiDailyStockAnalysis"),
    
    # 桌面端/Web 应用名
    ("ruyi-web", "ruyi-web"),
    ("ruyi_desktop", "ruyi_desktop"),
    ("ruyi-desktop", "ruyi-desktop"),
    ("ruyi_web", "ruyi_web"),
    
    # 项目短名
    ("Ruyi", "Ruyi"),
]

# 不需要修改的文件（二进制、依赖锁、数据库、git、构建产物、node_modules）
EXCLUDE_PREFIXES = (
    ".git/", ".venv/", "node_modules/", "logs/", "data/", "reports/",
    "__pycache__/", ".mypy_cache/", ".pytest_cache/",
    "static/",  # 构建产物不手动改
    "apps/ruyi-web/node_modules/",
    "apps/ruyi-desktop/node_modules/",
)
EXCLUDE_FILES = {
    "package-lock.json", ".dockerignore",
}


def should_exclude(rel: Path) -> bool:
    s = str(rel).replace("\\", "/")
    for p in EXCLUDE_PREFIXES:
        if s.startswith(p) or f"/{p}" in s:
            return True
    if rel.name in EXCLUDE_FILES:
        return True
    # 不处理二进制/ext
    if rel.suffix in (".png", ".jpg", ".gif", ".ico", ".svg", ".woff", ".ttf",
                      ".pyc", ".lock", ".csv", ".yaml", ".yml", ".db",
                      ".woff2", ".eot", ".otf"):
        return True
    return False


def rebrand_file(filepath: Path) -> tuple[int, str]:
    """Rebrand a file, return (change_count, first_change_log)."""
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return 0, ""
    
    changed = 0
    first_log = ""
    new_text = text
    for old, new in REPLACEMENTS:
        if old in new_text:
            # 对短名称 Ruyi → Ruyi 做精确匹配，避免替换单词内部
            if old == "Ruyi":
                new_text = re.sub(r'\bDSA\b', new, new_text)
                count = len(re.findall(r'\bDSA\b', text))
            else:
                new_text = new_text.replace(old, new)
                count = text.count(old)
            if count > 0:
                changed += count
                if not first_log:
                    first_log = f"'{old}' → '{new}' × {count}"
    
    if changed > 0:
        filepath.write_text(new_text, encoding="utf-8")
    return changed, first_log


def main():
    print("=" * 50)
    print("品牌化改造 — 如意金股 / RuyiDailyStockAnalysis")
    print("=" * 50)
    
    total_files = 0
    total_changes = 0
    logs = []
    
    for f in sorted(ROOT.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(ROOT)
        if should_exclude(rel):
            continue
        
        changes, log = rebrand_file(f)
        if changes > 0:
            total_files += 1
            total_changes += changes
            logs.append(f"  {rel} → {log}")
    
    print(f"\n修改了 {total_files} 个文件，共 {total_changes} 处替换\n")
    for l in logs:
        print(l)
    
    print(f"\n{'=' * 50}")
    print("改造完成！")


if __name__ == "__main__":
    main()