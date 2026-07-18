#!/usr/bin/env python3
"""Direct Tushare API connectivity test."""
import json, urllib.request, urllib.error, sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent.parent
lines = [l.strip() for l in (root / "key.txt").read_text("utf-8").splitlines() if l.strip()]
token = None
for i, l in enumerate(lines):
    if l == "Tushare" and i + 1 < len(lines):
        token = lines[i + 1]
        break
if not token: print("TUSHARE_TOKEN_MISSING"); sys.exit(1)

print(f"Token: {token[:8]}...{token[-4:]} ({len(token)} chars)")

# Test 1: trade_cal
payload = json.dumps({"api_name":"trade_cal","token":token,"params":{"exchange":"SSE","start_date":"20260701","end_date":"20260717"}}).encode()
req = urllib.request.Request("http://api.tushare.pro", data=payload,
    headers={"Content-Type":"application/json"}, method="POST")
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read().decode())
        if d.get("code") == 0:
            items = d["data"]["items"]
            print(f"trade_cal ✅  {len(items)} records")
            for row in items[:7]:
                print(f"  {row[0]}  {'OPEN' if row[1]=='1' else 'CLOSED'}")
        else:
            print(f"trade_cal ❌  code={d['code']}  {d.get('msg','')[:120]}")
except Exception as e:
    print(f"trade_cal ❌  {e}")

# Test 2: daily (if we got past step 1)
payload = json.dumps({"api_name":"daily","token":token,"params":{"ts_code":"000001.SZ","start_date":"20260701","end_date":"20260717"}}).encode()
req = urllib.request.Request("http://api.tushare.pro", data=payload,
    headers={"Content-Type":"application/json"}, method="POST")
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read().decode())
        if d.get("code") == 0:
            items = d["data"]["items"]
            print(f"daily    ✅  {len(items)} records")
            for row in items[:3]:
                print(f"  {row[1]}  O:{row[2]} H:{row[3]} L:{row[4]} C:{row[5]}")
        else:
            print(f"daily    ❌  code={d['code']}  {d.get('msg','')[:120]}")
except Exception as e:
    print(f"daily    ❌  {e}")