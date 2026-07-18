#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 API Key 是否可用（硅基流动 SiliconFlow + OpenAI 兼容格式）

用法:
    python scripts/test_api_key.py                              # 从 key.txt 读取
    python scripts/test_api_key.py --key sk-xxx                 # 直接传入
    python scripts/test_api_key.py --endpoint https://...       # 自定义端点
"""

import json
import sys
import urllib.request
import urllib.error
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_KEY_FILE = PROJECT_ROOT / "key.txt"
DEFAULT_ENDPOINT = "https://api.siliconflow.cn/v1/chat/completions"
TEST_MODEL = "Qwen/Qwen2.5-7B-Instruct"


def read_key(key_path=None):
    p = Path(key_path) if key_path else DEFAULT_KEY_FILE
    if not p.exists():
        print(f"❌ Key 文件不存在: {p}")
        sys.exit(1)
    key = p.read_text(encoding="utf-8").strip()
    if not key:
        print(f"❌ Key 文件为空: {p}")
        sys.exit(1)
    return key


def test_key(key, endpoint=None):
    url = endpoint or DEFAULT_ENDPOINT
    payload = json.dumps({
        "model": TEST_MODEL,
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 5,
    }).encode()

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode())
            if "choices" in body and body["choices"]:
                reply = body["choices"][0].get("message", {}).get("content", "")
                print(f"✅ Key 有效！响应: {reply[:80]}")
                return True
            else:
                print(f"⚠️  响应异常: {json.dumps(body, ensure_ascii=False)[:200]}")
                return False
    except urllib.error.HTTPError as e:
        err = e.read().decode(errors="replace")
        print(f"❌ Key 无效 (HTTP {e.code})")
        if err:
            try:
                msg = json.loads(err).get("error", {}).get("message", err)
                print(f"   错误: {msg[:200]}")
            except json.JSONDecodeError:
                print(f"   响应: {err[:200]}")
        else:
            www = e.headers.get("Www-Authenticate", "")
            if www:
                print(f"   {www}")
        return False
    except urllib.error.URLError as e:
        print(f"❌ 网络错误: {e.reason}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="测试 API Key 是否可用")
    parser.add_argument("--key", help="直接传入 Key（默认从 key.txt 读取）")
    parser.add_argument("--endpoint", help="自定义 API 端点")
    parser.add_argument("--file", help="指定 Key 文件路径")
    args = parser.parse_args()

    key = args.key or read_key(args.file)
    endpoint = args.endpoint or DEFAULT_ENDPOINT

    print(f"🔑 Key: {key[:8]}...{key[-4:]}")
    print(f"🎯 端点: {endpoint}")
    print(f"🤖 模型: {TEST_MODEL}")
    print()

    ok = test_key(key, endpoint)
    sys.exit(0 if ok else 1)