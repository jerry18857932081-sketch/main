"""
实时数据管道 — 直接调用东方财富/腾讯 HTTP API
绕过 akshare，速度更快、更可靠。
"""
import json
import logging
import re
import time
from datetime import datetime, timedelta
from typing import Optional

import requests
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ===== HTTP 工具 =====
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://quote.eastmoney.com/",
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

def _get(url: str, retries: int = 2) -> Optional[requests.Response]:
    for i in range(retries + 1):
        try:
            resp = SESSION.get(url, timeout=10)
            if resp.status_code == 200:
                return resp
        except Exception as e:
            if i == retries:
                logger.error(f"HTTP GET {url[:60]}: {e}")
            else:
                time.sleep(0.5)
    return None


# ===== 股票基础列表 =====

def _safe_f(v):
    """过滤 '-' 等无效值"""
    if v is None or v == "-" or v == "":
        return None
    try: return float(v)
    except: return None


def fetch_stock_list(session):
    """从东方财富获取全A股列表（分页拉取全部5000+只）"""
    from backend.database.models import StockUniverse

    fields = "f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f26,f22,f33,f11,f62,f128,f136,f115,f152"
    base = "https://push2.eastmoney.com/api/qt/clist/get"
    fs = "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23"
    page_size = 100
    total_count = 0

    # 先拿第一页获取总数
    url = f"{base}?pn=1&pz={page_size}&po=1&np=1&fltt=2&invt=2&fid=f12&fs={fs}&fields={fields}"
    resp = _get(url)
    if not resp:
        return 0
    try:
        data = resp.json().get("data", {})
        total = data.get("total", 0)
        items = data.get("diff", [])
    except:
        return 0

    total_pages = min((total // page_size) + 1, 60)  # 最多60页=6000只
    logger.info(f"获取股票列表: 共{total}只, {total_pages}页")

    for page in range(1, total_pages + 1):
        if page > 1:
            url = f"{base}?pn={page}&pz={page_size}&po=1&np=1&fltt=2&invt=2&fid=f12&fs={fs}&fields=f12,f14,f20"
            resp = _get(url)
            if not resp:
                continue
            try:
                items = resp.json().get("data", {}).get("diff", [])
            except:
                continue

        for item in items:
            code = str(item.get("f12", "")).strip()
            name = str(item.get("f14", "")).strip()
            if not code or not name:
                continue
            exchange = "SH" if code.startswith(("60", "68")) else "SZ" if code.startswith(("00", "30")) else "BJ"
            existing = session.query(StockUniverse).filter_by(code=code).first()
            if existing:
                existing.name = name; existing.exchange = exchange
                existing.market_cap = _safe_f(item.get("f20"))
                existing.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            else:
                session.add(StockUniverse(
                    code=code, name=name, exchange=exchange,
                    market_cap=_safe_f(item.get("f20")),
                    updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ))
            total_count += 1
        session.commit()
        time.sleep(0.3)  # 避免请求过快

    logger.info(f"股票列表入库: {total_count} 只")
    return total_count


# ===== 实时行情 =====

def fetch_spot_batch(session):
    """拉取全市场实时行情并写入 stock_spot"""
def fetch_spot_batch(session):
    """拉取全市场实时行情并写入 stock_spot（分页拉取全部）"""
    from backend.database.models import StockSpot

    def _sf(v):
        if v is None or v == "-" or v == "":
            return None
        try: return float(v)
        except: return None

    base = "https://push2.eastmoney.com/api/qt/clist/get"
    fs = "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23"
    fields = "f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f115,f152"
    page_size = 100
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    url = f"{base}?pn=1&pz={page_size}&po=1&np=1&fltt=2&invt=2&fid=f12&fs={fs}&fields={fields}"
    resp = _get(url)
    if not resp: return 0
    try:
        data = resp.json().get("data", {})
        total = data.get("total", 0)
        items = data.get("diff", [])
    except: return 0

    total_pages = min((total // page_size) + 1, 60)

    def _process(items):
        c = 0
        for item in items:
            code = str(item.get("f12", ""))
            if not code: continue
            price = _sf(item.get("f2"))
            if price is None: continue
            spot = session.query(StockSpot).filter_by(code=code).first()
            vals = {"name":str(item.get("f14","")),"current_price":price,"change_pct":_sf(item.get("f3")),"change_amount":_sf(item.get("f4")),"volume":_sf(item.get("f5")),"turnover":_sf(item.get("f6")),"turnover_rate":_sf(item.get("f8")),"amplitude":_sf(item.get("f7")),"high":_sf(item.get("f15")),"low":_sf(item.get("f16")),"open":_sf(item.get("f17")),"prev_close":_sf(item.get("f18")),"pe_ttm":_sf(item.get("f115")),"pb":_sf(item.get("f23")),"fetched_at":now}
            if spot:
                for k,v in vals.items():
                    if v is not None: setattr(spot,k,v)
            else: session.add(StockSpot(code=code,**vals))
            c += 1
        return c

    count = _process(items)
    for page in range(2, total_pages + 1):
        url = f"{base}?pn={page}&pz={page_size}&po=1&np=1&fltt=2&invt=2&fid=f12&fs={fs}&fields={fields}"
        resp = _get(url)
        if not resp: continue
        try: items = resp.json().get("data",{}).get("diff",[])
        except: continue
        count += _process(items)
        session.commit()
        time.sleep(0.3)

    session.commit()
    logger.info(f"行情快照: {count} 只")
    return count


# ===== 日K线（腾讯财经） =====

def fetch_kline(code: str, days: int = 250, session=None) -> int:
    """从腾讯财经拉取个股日K线（前复权）"""
    prefix = "sh" if code.startswith(("60", "68")) else "sz"
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={prefix}{code},day,,,{days},qfq"
    resp = _get(url)
    if not resp:
        return 0

    try:
        data = resp.json().get("data", {})
        stock_data = data.get(f"{prefix}{code}", {})
        klines = stock_data.get("qfqday", stock_data.get("day", []))
    except Exception:
        return 0

    if not klines:
        return 0

    from backend.database.models import StockDaily
    count = 0
    for line in klines:
        if len(line) < 6:
            continue
        date_str = str(line[0])
        open_ = float(line[1])
        close_ = float(line[2])
        high = float(line[3])
        low = float(line[4])
        vol = float(line[5])
        existing = session.query(StockDaily).filter_by(code=code, trade_date=date_str).first()
        if not existing:
            session.add(StockDaily(
                code=code, trade_date=date_str,
                open=open_, close=close_,
                high=high, low=low,
                volume=vol, turnover=0,
                change_pct=round((close_-open_)/open_*100, 2) if open_ else 0,
            ))
            count += 1
    session.commit()
    return count


# ===== 分时数据 =====

def fetch_intraday(code: str, session=None) -> list:
    """从东方财富拉取当日分时数据"""
    market = 1 if code.startswith(("60", "68")) else 0
    secid = f"{market}.{code}"
    url = f"https://push2.eastmoney.com/api/qt/stock/trends2/get?secid={secid}&fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57&ndays=1"
    resp = _get(url)
    if not resp:
        return []

    try:
        trends = resp.json().get("data", {}).get("trends", [])
    except Exception:
        return []

    if not trends:
        return []

    from backend.database.models import StockIntraday
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    records = []
    for line in trends:
        parts = line.split(",")
        if len(parts) < 7:
            continue
        time_str, price, _, avg_price, vol, turnover = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
        if not time_str or float(price) == 0:
            continue
        # time_str 可能已包含日期前缀，清洗只取时间部分
        if len(time_str) > 10:
            time_str = time_str[-8:]  # 取末尾 HH:MM:SS
        today = datetime.now().strftime('%Y-%m-%d')
        full_time = f"{today} {time_str}"
        existing = session.query(StockIntraday).filter_by(code=code, time=full_time).first()
        if not existing:
            session.add(StockIntraday(
                code=code, time=full_time,
                price=float(price), avg_price=float(avg_price) if avg_price != '-' else float(price),
                volume=float(vol or 0), turnover=float(turnover or 0),
                fetched_at=now,
            ))
        records.append({"time": full_time, "price": float(price), "avg_price": float(avg_price) if avg_price != '-' else float(price),
                         "volume": float(vol or 0), "turnover": float(turnover or 0)})
    session.commit()
    return records


# ===== 盘口 =====

def fetch_depth(code: str, session=None) -> Optional[dict]:
    """从东方财富拉取盘口五档"""
    market = 1 if code.startswith(("60", "68")) else 0
    secid = f"{market}.{code}"
    url = f"https://push2.eastmoney.com/api/qt/stock/get?secid={secid}&fields=f19,f20,f21,f22,f23,f24,f25,f26,f27,f28,f29,f30,f31,f32,f33,f34,f35,f36,f37,f38,f39,f40"
    resp = _get(url)
    if not resp:
        return None

    try:
        d = resp.json().get("data", {})
    except Exception:
        return None

    asks = []
    bids = []
    for i in range(1, 6):
        ask_p = d.get(f"f{18+i*2}")
        ask_v = d.get(f"f{19+i*2}")
        bid_p = d.get(f"f{28+i*2}")
        bid_v = d.get(f"f{29+i*2}")
        if ask_p and ask_p != "-":
            asks.append({"price": float(ask_p), "volume": float(ask_v or 0)})
        if bid_p and bid_p != "-":
            bids.append({"price": float(bid_p), "volume": float(bid_v or 0)})

    return {"asks": asks, "bids": bids} if asks or bids else None


# ===== 批量初始化 =====

def seed_real(session):
    """用真实HTTP API初始化数据"""
    logger.info("开始拉取真实数据...")
    n = fetch_stock_list(session)
    if n == 0:
        logger.warning("股票列表拉取失败")
        return
    n_spot = fetch_spot_batch(session)
    logger.info(f"数据初始化完成: {n} 只股票, {n_spot} 条行情")

    # 拉取几只核心股票的K线+分时
    sample_codes = ["600519", "000858", "300750", "601138", "300308", "002472"]
    for code in sample_codes:
        try:
            n_k = fetch_kline(code, days=250, session=session)
            n_i = len(fetch_intraday(code, session=session) or [])
            logger.info(f"  {code}: K线{n_k}条, 分时{n_i}条")
            time.sleep(0.3)
        except Exception as e:
            logger.error(f"  {code} 失败: {e}")
