#!/usr/bin/env python3
"""列出项目中与新闻/股票/搜索相关的 API 端点。"""
import sys
import urllib.request
import json


def main():
    try:
        r = urllib.request.urlopen("http://10.39.41.245:8000/openapi.json", timeout=5)
        spec = json.loads(r.read())
    except Exception as e:
        print(f"❌ 无法获取 OpenAPI spec: {e}")
        sys.exit(1)

    keywords = ["stock", "news", "search", "intel", "intelligence", "history"]
    news_paths = [
        p for p in spec["paths"].keys()
        if any(kw in p.lower() for kw in keywords)
    ]

    print("=== Relevant API endpoints ===")
    for p in sorted(set(news_paths)):
        methods = list(spec["paths"][p].keys())
        print(f"  {p} [{','.join(methods)}]")


if __name__ == "__main__":
    main()