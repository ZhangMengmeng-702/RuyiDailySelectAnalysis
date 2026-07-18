#!/usr/bin/env python3
"""通过 API 获取贵州茅台新闻并触发分析。"""
import subprocess, json, sys

HOST = "http://10.39.41.245:8000"
STOCK = "600519"


def curl(method, path, data=None):
    cmd = ["curl", "-s", "--max-time", "30", "-X", method, f"{HOST}{path}",
           "-H", "Content-Type: application/json"]
    if data:
        cmd += ["-d", json.dumps(data, ensure_ascii=False)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return r.stdout


def main():
    print("=== 1. Getting news via agent/research ===")
    result = curl("POST", "/api/v1/agent/research", {
        "question": f"贵州茅台 {STOCK} 最新新闻 2026年7月",
        "stock_code": STOCK,
        "max_results": 5,
    })
    try:
        data = json.loads(result)
        print(json.dumps(data, ensure_ascii=False, indent=2)[:1500])
    except Exception:
        print(result[:500])

    print("\n=== 2. Latest history news ===")
    result = curl("GET", "/api/v1/history?page=1&limit=3")
    try:
        data = json.loads(result)
        items = data.get("items", [])
        if items:
            latest_id = items[0]["id"]
            news = curl("GET", f"/api/v1/history/{latest_id}/news?limit=5")
            print(f"News for analysis #{latest_id}: {news[:500]}")
    except Exception:
        print(result[:200])

    print("\n=== 3. Triggering analysis for 600519 ===")
    result = curl("POST", "/api/v1/analysis/analyze", {
        "stock_codes": [STOCK],
        "force_refresh": True,
        "send_notification": False,
    })
    try:
        data = json.loads(result)
        print(f"Analysis triggered: qid={data.get('query_id','?')[:20]}")
    except Exception:
        print(result[:200])


if __name__ == "__main__":
    main()
    print("\nDone! Check the browser for results.")