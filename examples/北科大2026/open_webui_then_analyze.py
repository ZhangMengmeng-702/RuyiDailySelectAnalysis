#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化流程：AdsPower 浏览器 → 打开 WebUI → 分析贵州茅台(600519) → 查看结果
"""

import asyncio, json, sys, urllib.request, urllib.error
from pathlib import Path

API_BASE = "http://127.0.0.1:8000"
ADSPOWER_API = "http://127.0.0.1:50325"
USER_ID = "k1epmwka"
STOCK_CODE = "600519"


def fetch_adspower_ws() -> str:
    req = urllib.request.Request(
        f"{ADSPOWER_API}/api/v1/browser/start?user_id={USER_ID}",
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    ws = data["data"]["ws"]["puppeteer"]
    print(f"  ✅ AdsPower → port {data['data']['debug_port']}")
    return ws


async def cdp_send(ws, msg_id: int, method: str, params: dict = None) -> dict:
    await ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
    resp = json.loads(await ws.recv())
    if resp.get("error"):
        print(f"  ⚠️  CDP [{method}]: {resp['error']['message']}")
    return resp


async def main():
    # ── Step 0: verify server ──
    print("=" * 55)
    print("0/5: 验证 Web 服务")
    try:
        r = urllib.request.urlopen(f"{API_BASE}/api/health", timeout=5)
        h = json.loads(r.read())
        assert h.get("status") == "ok"
        print(f"  ✅ {json.dumps(h, ensure_ascii=False)}")
    except Exception as e:
        print(f"  ❌ 服务不可用: {e}")
        sys.exit(1)

    # ── Step 1: get WS ──
    print("\n1/5: 获取 AdsPower WS 端点")
    try:
        WS_URL = fetch_adspower_ws()
    except Exception as e:
        print(f"  ⚠️  {e}，使用缓存 URL")
        WS_URL = "ws://127.0.0.1:60365/devtools/browser/02f930fd-0088-42fd-8c4d-13015518c18b"

    # ── Step 2: open WebUI ──
    print("\n2/5: 在浏览器中打开 WebUI")
    try:
        import websockets
        async with websockets.connect(WS_URL, max_size=2**20) as ws:
            resp = await cdp_send(ws, 1, "Target.createTarget",
                                  {"url": f"{API_BASE}/"})
            tid = resp.get("result", {}).get("targetId", "?")
            print(f"  ✅ WebUI 已打开 → targetId={tid[:20]}...")
            await asyncio.sleep(2)

            # ── Step 3: trigger analysis ──
            print("\n3/5: 触发 600519(贵州茅台) 分析")
            payload = json.dumps({
                "stock_codes": [STOCK_CODE],
                "force_refresh": True,
                "send_notification": False,
            }).encode("utf-8")

            req = urllib.request.Request(
                f"{API_BASE}/api/v1/analysis/analyze",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=300) as r:
                    result = json.loads(r.read())
                    print(f"  ✅ 任务已提交 → "
                          f"{json.dumps(result, ensure_ascii=False)[:200]}")
            except urllib.error.HTTPError as e:
                body = e.read().decode(errors="replace")
                print(f"  ⚠️  API {e.code}: {body[:200]}")

            # ── Step 4: open history ──
            print("\n4/5: 打开历史报告页")
            await cdp_send(ws, 2, "Target.createTarget",
                           {"url": f"{API_BASE}/history"})
            print("  ✅ 历史报告页面已打开")

    except ImportError:
        print("  ⚠️  未安装 websockets，跳过浏览器操作")
    except Exception as e:
        print(f"  ⚠️  浏览器异常: {type(e).__name__}: {e}")

    # ── Step 5: verify result via API ──
    print("\n5/5: 验证分析结果")
    try:
        r = urllib.request.urlopen(
            f"{API_BASE}/api/v1/history?page=1&limit=5", timeout=15)
        data = json.loads(r.read())
        items = data if isinstance(data, list) else \
            data.get("data", data.get("items", []))
        if items:
            print(f"  ✅ 共 {len(items)} 条记录")
            for rec in items[:5]:
                code = rec.get("code") or rec.get("stock_code", "?")
                advice = rec.get("operation_advice") or rec.get("advice", "?")
                score = rec.get("sentiment_score") or rec.get("score", "?")
                dt = str(rec.get("analysis_date") or rec.get("date", "?"))[:10]
                trend = rec.get("trend_prediction") or rec.get("trend", "")
                print(f"    📈 {code} | {dt} | 评分:{score} | {advice} | {trend}")
        else:
            print("  ⚠️  暂无分析记录")
    except Exception as e:
        print(f"  ⚠️  查询历史失败: {e}")

    print("\n" + "=" * 55)
    print("✅ 流程完成！浏览器中可见 WebUI + 历史报告页")


if __name__ == "__main__":
    asyncio.run(main())