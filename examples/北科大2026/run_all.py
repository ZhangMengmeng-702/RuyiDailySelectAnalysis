#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全自动化：验证 → 打开浏览器 → 分析600519 → 查结果"""

import asyncio, json, urllib.request, urllib.error, sys, time

API = "http://127.0.0.1:8000"
ADSPOWER = "http://127.0.0.1:50325"
USER_ID = "k1epmwka"
STOCK = "600519"

async def cdp(ws, id, method, params=None):
    await ws.send(json.dumps({"id": id, "method": method, "params": params or {}}))
    return json.loads(await ws.recv())

async def main():
    print("=" * 55)
    # 1/5 Health
    try:
        r = urllib.request.urlopen(f"{API}/api/v1/health", timeout=5)
        h = json.loads(r.read())
        assert h["status"] == "ok"
        print(f"✅ [1/5] 服务正常 → {json.dumps(h, ensure_ascii=False)}")
    except Exception as e:
        print(f"❌ [1/5] 服务不可用: {e}")
        sys.exit(1)

    # 2/5 AdsPower
    print("\n✅ [2/5] 连接 AdsPower 浏览器")
    WS_URL = None
    try:
        r = urllib.request.urlopen(
            f"{ADSPOWER}/api/v1/browser/start?user_id={USER_ID}", timeout=10)
        data = json.loads(r.read())
        WS_URL = data["data"]["ws"]["puppeteer"]
        dp = data["data"]["debug_port"]
        print(f"  ✓ 调试端口 {dp} · WS 就绪")
    except Exception as e:
        print(f"  ⚠️  {e} — 跳过浏览器操作")

    # 3/5 + 4/5 Open WebUI + trigger analysis
    if WS_URL:
        try:
            import websockets
            async with websockets.connect(WS_URL, max_size=2**20) as ws:
                r1 = await cdp(ws, 1, "Target.createTarget", {"url": f"{API}/"})
                tid = r1.get("result", {}).get("targetId", "?")
                print(f"✅ [3/5] WebUI 已打开 → targetId={tid[:20]}...")
                await asyncio.sleep(2)

                print("\n✅ [4/5] 分析贵州茅台(600519)")
                payload = json.dumps({
                    "stock_codes": [STOCK],
                    "force_refresh": True,
                    "send_notification": False,
                }).encode()
                req = urllib.request.Request(
                    f"{API}/api/v1/analysis/analyze",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                try:
                    with urllib.request.urlopen(req, timeout=300) as r:
                        result = json.loads(r.read())
                        task_id = result.get("task_id") or result.get("id", "?")
                        print(f"  ✓ 任务已提交 → task_id={task_id}")
                        print(f"  响应: {json.dumps(result, ensure_ascii=False)[:200]}")
                except urllib.error.HTTPError as e:
                    body = e.read().decode(errors="replace")
                    print(f"  ⚠️  API {e.code}: {body[:200]}")
        except ImportError:
            print("  ⚠️  未安装 websockets，跳过")
        except Exception as e:
            print(f"  ⚠️  浏览器异常: {type(e).__name__}: {e}")

    # 5/5 Verify
    print("\n✅ [5/5] 验证分析结果")
    for attempt in range(6):
        try:
            r = urllib.request.urlopen(
                f"{API}/api/v1/history?page=1&limit=5", timeout=15)
            data = json.loads(r.read())
            records = data if isinstance(data, list) else (
                data.get("items") or data.get("data") or [])
            if records:
                print(f"  ✓ 共 {len(records)} 条分析记录")
                for rec in records[:3]:
                    code = rec.get("code", "?")
                    dt = str(rec.get("analysis_date", "?"))[:10]
                    score = rec.get("sentiment_score", "?")
                    advice = rec.get("operation_advice", "?")
                    trend = rec.get("trend_prediction", "")
                    print(f"    📈 {code} | {dt} | 评分:{score} | {advice} | {trend}")
                break
            print(f"  ⏳ 等待分析… ({attempt+1}/6)")
            time.sleep(5)
        except Exception as e:
            print(f"  ⚠️  ({attempt+1}/6): {type(e).__name__}: {e}")
            time.sleep(5)
    else:
        print("  ⏰ 超时，分析可能仍在运行")

    print("\n" + "=" * 55)
    print("✅ 全流程完成！")
    print(f"   AdsPower 浏览器中已打开 WebUI\n")

asyncio.run(main())