#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全自动化：API调用 + CDP浏览器控制"""
import asyncio, json, sys, os, time, subprocess

API = "http://127.0.0.1:8000"
ADSP = "http://127.0.0.1:50325"
UID = "k1epmwka"

async def cdp(ws, mid, method, params=None):
    await ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
    return json.loads(await ws.recv())

async def main():
    print("=" * 55)

    # 1/5 Health
    print("[1/5] 健康检查")
    r = subprocess.run(["curl", "-s", "--max-time", "3", f"{API}/api/v1/health"],
                       capture_output=True, text=True)
    if '"status":"ok"' not in r.stdout:
        print(f"  ❌ 服务不可用: {r.stdout[:100]}"); sys.exit(1)
    print(f"  ✅ {r.stdout.strip()}")

    # 2/5 AdsPower
    print("\n[2/5] AdsPower 浏览器")
    r = subprocess.run(["curl", "-s", "--max-time", "5",
                        f"{ADSP}/api/v1/browser/start?user_id={UID}"],
                       capture_output=True, text=True)
    data = json.loads(r.stdout)
    WS_URL = data["data"]["ws"]["puppeteer"]
    DPORT = data["data"]["debug_port"]
    print(f"  ✅ 调试端口: {DPORT}")

    # 3/5 Open WebUI + trigger + history
    print("\n[3/5] 打开 WebUI 并提交分析")
    import websockets
    async with websockets.connect(WS_URL, max_size=2**20) as ws:
        resp = await cdp(ws, 1, "Target.createTarget", {"url": f"{API}/"})
        tid = resp.get("result", {}).get("targetId", "?")
        print(f"  ✅ WebUI 已打开 (targetId={tid[:20]}...)")
        await asyncio.sleep(2)

        # 4/5 Trigger analysis
        print("\n[4/5] 分析 600519 (贵州茅台)")
        payload = json.dumps({
            "stock_codes": ["600519"],
            "force_refresh": True,
            "send_notification": False,
        })
        r = subprocess.run(["curl", "-s", "--max-time", "300", "-X", "POST",
                           f"{API}/api/v1/analysis/analyze",
                           "-H", "Content-Type: application/json",
                           "-d", payload],
                          capture_output=True, text=True)
        result = json.loads(r.stdout)
        qid = result.get("query_id", "?")
        print(f"  ✅ 分析已提交 (query_id={qid})")

        # Open history page
        await cdp(ws, 2, "Target.createTarget", {"url": f"{API}/api/v1/history"})
        print("\n[5/5] 历史报告页已打开")

    # Verify
    for attempt in range(6):
        time.sleep(5)
        r = subprocess.run(["curl", "-s", "--max-time", "10",
                           f"{API}/api/v1/history?page=1&limit=5"],
                          capture_output=True, text=True)
        data = json.loads(r.stdout)
        items = data if isinstance(data, list) else data.get("items", data.get("data", []))
        if items and len(items) > 1:
            print(f"\n  共 {len(items)} 条分析记录:")
            for rec in items[:3]:
                code = rec.get("stock_code", "?")
                dt = str(rec.get("created_at", "?"))[:10]
                score = rec.get("sentiment_score", "?")
                advice = rec.get("operation_advice", "?")
                trend = rec.get("trend_prediction", "")
                print(f"    📈 {code} | {dt} | 评分:{score} | {advice} | {trend}")
            break
        print(f"  ⏳ 等待分析… ({attempt+1}/6)")
    else:
        print("  ⏰ 超时")

    print("\n" + "=" * 55)
    print("✅ 全流程自动化完成！")
    print(f"   AdsPower 浏览器中: WebUI + 历史报告页已打开")

asyncio.run(main())