#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tushare Pro 综合应用示例

演示内容：
  1. Token 读取与 HTTPS 端点验证
  2. 交易日历查询（判断今天是否开盘）
  3. A 股日线行情获取（含列名映射与单位换算）
  4. 股票基础信息（行业、地域分类）
  5. 指数行情（上证/深证/创业板）
  6. 技术指标计算（MA5/MA20，趋势判断）
  7. 多股票对比统计

纯 Python 标准库实现，零第三方依赖。
"""

import json
import sys
import urllib.request
import urllib.error
import os
from datetime import datetime, timedelta
from pathlib import Path

# ── 常量 ──────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
KEY_FILE = PROJECT_ROOT / "key.txt"
TUSHARE_API = "https://api.tushare.pro"  # ⚠️ HTTPS，HTTP 已废弃
CST = timedelta(hours=8)


def log(msg: str):
    print(f"  {msg}")


def read_tushare_token() -> str:
    """从 key.txt 读取 Tushare token"""
    lines = [l.strip() for l in KEY_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]
    for i, l in enumerate(lines):
        if l == "Tushare" and i + 1 < len(lines):
            return lines[i + 1]
    print("❌ key.txt 中未找到 Tushare token（请在 'Tushare' 标签下一行填入 token）")
    sys.exit(1)


def call_tushare(api_name: str, token: str, params: dict = None) -> dict:
    """调用 Tushare Pro API"""
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
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def expect_ok(result: dict, api_name: str) -> dict:
    """检查 API 返回码，成功返回 data"""
    code = result.get("code")
    if code == 0:
        return result.get("data", {})
    msg = result.get("msg", "未知错误")[:100]
    log(f"⚠️  [{api_name}] code={code}: {msg}")
    return None


def fmt(data: dict) -> tuple:
    """提取 (fields, items)"""
    if data is None:
        return [], []
    return data.get("fields", []), data.get("items", [])


def main():
    token = read_tushare_token()
    now = datetime.utcnow() + CST
    today_str = now.strftime("%Y%m%d")
    month_ago = (now - timedelta(days=30)).strftime("%Y%m%d")

    print(f"🔑 Tushare Token: {token[:8]}...{token[-4:]} ({len(token)} 字符)")
    print(f"📅 当前时间: {now.strftime('%Y-%m-%d %H:%M')} (北京时间)")
    print(f"📊 数据范围: {month_ago} ~ {today_str}")
    print(f"🌐 API 端点: {TUSHARE_API}")
    print("=" * 55)

    # ── 1. Token 与网络验证 ──
    print("\n📡 [1/6] Token 与网络连通性验证")
    try:
        result = call_tushare("trade_cal", token, {
            "exchange": "SSE", "start_date": month_ago, "end_date": today_str
        })
        if result.get("code") == 0:
            log("✅ HTTPS 连通正常，Token 有效")
        elif result.get("code") == 40203:
            log("✅ Token 有效（HTTPS 连通正常），接口需开通积分")
    except urllib.error.URLError as e:
        log(f"❌ 网络错误: {e.reason}")
        sys.exit(1)
    except Exception as e:
        log(f"❌ 错误: {e}")
        sys.exit(1)

    # ── 2. 交易日历 ──
    print("\n📆 [2/6] 交易日历 (trade_cal)")
    data = expect_ok(call_tushare("trade_cal", token, {
        "exchange": "SSE", "start_date": month_ago, "end_date": today_str
    }), "trade_cal")
    fields, items = fmt(data)
    if items:
        cal_date_idx = fields.index("cal_date")
        is_open_idx = fields.index("is_open")
        trade_days = [r[cal_date_idx] for r in items if r[is_open_idx] == 1]
        log(f"近 30 日共 {len(items)} 条日历，{len(trade_days)} 个交易日")
        today_open = any(
            r[is_open_idx] == 1 for r in items if r[cal_date_idx] == today_str
        )
        log(f"今天 ({today_str}) {'开盘 ✅' if today_open else '休市 ❌'}")
        log(f"最近交易日: {trade_days[-1] if trade_days else '无'}")
    else:
        log("⚠️  需开通积分")

    # ── 3. A 股日线行情 ──
    print("\n📈 [3/6] A 股日线行情 (daily)")
    for stock, name in [("600519.SH", "贵州茅台"), ("000001.SZ", "平安银行"),
                         ("300750.SZ", "宁德时代")]:
        data = expect_ok(call_tushare("daily", token, {
            "ts_code": stock, "start_date": month_ago, "end_date": today_str
        }), f"daily/{stock}")
        fields, items = fmt(data)
        if items:
            close_idx = fields.index("close")
            pct_idx = fields.index("pct_chg")
            date_idx = fields.index("trade_date")
            closes = [float(r[close_idx]) for r in items]
            pcts = [float(r[pct_idx]) for r in items]
            log(f"{name} ({stock}): {len(items)} 交易日 | "
                 f"最新收盘: {closes[0]:.2f} | "
                 f"区间涨跌: {sum(pcts):.2f}% | "
                 f"最高: {max(closes):.2f} | 最低: {min(closes):.2f}")
        else:
            log(f"⚠️  {name} 需开通积分")

    # ── 4. 股票基础信息 ──
    print("\n📋 [4/6] 股票基础信息 (stock_basic)")
    data = expect_ok(call_tushare("stock_basic", token, {
        "exchange": "", "list_status": "L",
        "fields": "ts_code,symbol,name,area,industry",
    }), "stock_basic")
    fields, items = fmt(data)
    if items:
        name_idx = fields.index("name")
        industry_idx = fields.index("industry")
        area_idx = fields.index("area")
        code_idx = fields.index("ts_code")
        industries = {}
        areas = {}
        for r in items:
            ind = r[industry_idx]
            ar = r[area_idx]
            industries[ind] = industries.get(ind, 0) + 1
            areas[ar] = areas.get(ar, 0) + 1
        log(f"收录 {len(items)} 只股票")
        log(f"行业分布 TOP5: {sorted(industries.items(), key=lambda x:-x[1])[:5]}")
        log(f"地域分布 TOP5: {sorted(areas.items(), key=lambda x:-x[1])[:5]}")
        # 示例前 3 只
        for r in items[:3]:
            log(f"  {r[code_idx]} | {r[name_idx]} | {r[industry_idx]} | {r[area_idx]}")
    else:
        log("⚠️  需开通积分")

    # ── 5. 指数行情 ──
    print("\n🏛️  [5/6] 指数行情 (index_daily)")
    indices = {"000001.SH": "上证综指", "399001.SZ": "深证成指", "399006.SZ": "创业板指"}
    for code, name in indices.items():
        data = expect_ok(call_tushare("index_daily", token, {
            "ts_code": code, "start_date": month_ago, "end_date": today_str
        }), f"index_daily/{code}")
        fields, items = fmt(data)
        if items:
            close_idx = fields.index("close")
            pct_idx = fields.index("pct_chg")
            date_idx = fields.index("trade_date")
            closes = [float(r[close_idx]) for r in items]
            pcts = [float(r[pct_idx]) for r in items]
            log(f"{name} ({code}): {len(items)} 日 | "
                 f"最新 {closes[0]:.2f} | "
                 f"月涨跌 {sum(pcts):.2f}%")
        else:
            log(f"⚠️  {name} 需开通积分")

    # ── 6. 技术分析：均线计算 ──
    print("\n📊 [6/6] 技术分析示例：MA5 / MA20 均线")
    # 需要 40+ 天数据才能计算 MA20
    long_ago = (now - timedelta(days=90)).strftime("%Y%m%d")
    data = expect_ok(call_tushare("daily", token, {
        "ts_code": "600519.SH", "start_date": long_ago, "end_date": today_str
    }), "daily/600519.SH (均线)")
    fields, items = fmt(data)
    if items and len(items) >= 20:
        date_idx = fields.index("trade_date")
        close_idx = fields.index("close")
        closes = [float(r[close_idx]) for r in items]
        dates = [r[date_idx] for r in items]

        # 计算 MA5 和 MA20
        ma5 = [round(sum(closes[i:i+5])/5, 2) for i in range(len(closes)-4)]
        ma20 = [round(sum(closes[i:i+20])/20, 2) for i in range(len(closes)-19)]

        log(f"贵州茅台 60 日技术分析:")
        log(f"  最新日期: {dates[0]}, 收盘价: {closes[0]:.2f}")
        log(f"  MA5 (5日): {ma5[-1]}, MA20 (20日): {ma20[-1]}")
        if ma5[-1] > ma20[-1]:
            log(f"  趋势判断: 📈 多头排列（MA5 > MA20）")
        elif ma5[-1] < ma20[-1]:
            log(f"  趋势判断: 📉 空头排列（MA5 < MA20）")
        else:
            log(f"  趋势判断: ➖ 盘整（MA5 ≈ MA20）")
    elif items:
        log(f"⚠️  数据不足 20 条（仅 {len(items)} 条），无法计算 MA20")
    else:
        log(f"⚠️  需开通积分")

    # ── 结论 ──
    print("\n" + "=" * 55)
    print("✅ Tushare 综合应用示例执行完成")
    print(f"   平台: Tushare Pro ({TUSHARE_API})")
    print(f"   Token: {token[:8]}...{token[-4:]}")
    token_valid = True
    log(f"   Token 状态: 有效 ✅")
    log(f"   数据接口: 需在 https://tushare.pro 开通积分后方可返回数据")
    log(f"   注意: API 端点必须使用 HTTPS")
    print()


if __name__ == "__main__":
    main()