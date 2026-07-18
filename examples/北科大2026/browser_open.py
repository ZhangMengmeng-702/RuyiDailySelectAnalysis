"""仅用于浏览器 CDP 操作的 Python 脚本（WS + Target.createTarget）"""
import asyncio, json, sys

WS_URL = sys.argv[1] if len(sys.argv) > 1 else None
URLS = sys.argv[2:] if len(sys.argv) > 2 else []

if not WS_URL or not URLS:
    print("Usage: python browser_open.py WS_URL URL1 [URL2...]")
    sys.exit(1)

async def main():
    import websockets
    async with websockets.connect(WS_URL, max_size=2**20) as ws:
        for i, url in enumerate(URLS):
            await ws.send(json.dumps({
                "id": i + 1, "method": "Target.createTarget",
                "params": {"url": url}
            }))
            resp = json.loads(await ws.recv())
            tid = resp.get("result", {}).get("targetId", "?")
            print(f"✅ [{i+1}] {url} → targetId={tid[:20]}...")
        await asyncio.sleep(1)

asyncio.run(main())