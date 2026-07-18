#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证 Tushare Pro Token 是否可用。

用法:
    python examples/北科大2026/05_test_Tushare_key.py
    python examples/北科大2026/05_test_Tushare_key.py --token xxx

验证策略（纯标准库，无需安装 tushare SDK）:
    1. 验证 Token 格式
    2. 测试 HTTPS 网络连通性
    3. 检测接口可用状态

注意: API 端点必须使用 HTTPS (https://api.tushare.pro)
"""

import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
KEY_FILE = PROJECT_ROOT / "key.txt"
TUSHARE_API = "https://api.tushare.pro"


def call_tushare(api_name: str, token: str, params: dict = None) -> dict:
    payload = json.dumps({
        "api_name": api_name,
        "token": token,
        "params": params or {},
    }).encode("utf-8")
    req = urllib.request.Request(
        TUSHARE_API,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def test_token(token: str) -> bool:
    ok = True

    # 1. 格式检查
    print(f"🔑 Token: {token[:8]}...{token[-4:]} ({len(token)} 字符)")
    if not token or len(token) < 30:
        print("  ❌ Token 格式异常")
        return False
    print("  ✅ Token 格式正确")
    print()

    # 2. HTTPS 连通性 + 认证检测
    print("📡 检测 Token 有效性...")
    try:
        result = call_tushare("trade_cal", token, {
            "exchange": "SSE",
            "start_date": "20260701",
            "end_date": "20260717",
        })
        code = result.get("code")
        if code == 0:
            print("  ✅ Token 有效 ✅ 接口可用（数据已返回）")
        elif code == 40203:
            msg = result.get("msg", "")[:80]
            print(f"  ✅ Token 有效 ✅（HTTPS 连通正常）")
            print(f"  ⚠️  接口需在 https://tushare.pro 开通积分: {msg}")
        elif code in (40101,):
            print(f"  ❌ API 请求格式错误 (code={code})")
            print(f"    请确认使用 HTTPS 端点: {TUSHARE_API}")
            ok = False
        else:
            print(f"  ❌ Token 异常 (code={code}): {result.get('msg', '')[:100]}")
            ok = False
    except urllib.error.HTTPError as e:
        print(f"  ❌ HTTP {e.code}: Token 可能无效")
        ok = False
    except urllib.error.URLError as e:
        print(f"  ❌ 网络错误: {e.reason}")
        print(f"    请检查能否访问 {TUSHARE_API}")
        ok = False
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        ok = False

    print()
    if ok:
        print("✅ 结论: Tushare Token 有效")
        print("   提示: 如需返回数据，请在 https://tushare.pro 开通接口积分")
    else:
        print("❌ 结论: Token 异常，请检查后重试")
    return ok


def read_token():
    lines = [l.strip() for l in KEY_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]
    for i, l in enumerate(lines):
        if l == "Tushare" and i + 1 < len(lines):
            return lines[i + 1]
    print("❌ 在 key.txt 中未找到 Tushare token（请在 'Tushare' 标签下一行填入 token）")
    sys.exit(1)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="验证 Tushare Pro Token")
    parser.add_argument("--token", help="直接传入 token")
    parser.add_argument("--file", help="指定 key 文件路径")
    args = parser.parse_args()

    if args.token:
        token = args.token
    else:
        token = read_token()

    ok = test_token(token)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()