"""数据管道 — 通过akshare拉取A股数据并写入SQLite"""
import time
import logging
from datetime import datetime
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

# ========== 帮助函数 ==========

def _safe_float(val, default=None):
    """安全转为float"""
    try:
        v = float(val)
        if pd.isna(v):
            return default
        return v
    except (ValueError, TypeError):
        return default


def _safe_int(val, default=0):
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return default


def _now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ========== 股票基础信息 ==========

def fetch_stock_universe(session, rate_limit: float = 0.5):
    """
    获取全部A股列表并写入 stock_universe 表。
    使用 akshare stock_info_a_code_name()。
    """
    try:
        import akshare as ak
        df = ak.stock_info_a_code_name()
    except Exception as e:
        logger.error(f"获取股票列表失败: {e}")
        return 0

    from backend.database.models import StockUniverse

    count = 0
    for _, row in df.iterrows():
        code = str(row.get("code", "")).strip()
        name = str(row.get("name", "")).strip()
        if not code or not name:
            continue
        # code 可能带交易所前缀，清洗
        exchange = ""
        if code.startswith("SH"):
            exchange = "SH"
            code = code[2:]
        elif code.startswith("SZ"):
            exchange = "SZ"
            code = code[2:]
        elif code.startswith("BJ"):
            exchange = "BJ"
            code = code[2:]
        # 判断交易所
        if not exchange:
            if code.startswith(("60", "68")):
                exchange = "SH"
            elif code.startswith(("00", "30")):
                exchange = "SZ"
            elif code.startswith(("83", "87", "43")):
                exchange = "BJ"

        existing = session.query(StockUniverse).filter_by(code=code).first()
        if existing:
            existing.name = name
            existing.exchange = exchange
            existing.updated_at = _now_str()
        else:
            session.add(StockUniverse(
                code=code,
                name=name,
                exchange=exchange,
                updated_at=_now_str(),
            ))
        count += 1

    session.commit()
    logger.info(f"股票列表已更新: {count} 只")
    return count


# ========== 实时行情 ==========

def fetch_spot_data(session):
    """
    获取全市场实时行情快照。
    使用 akshare stock_zh_a_spot_em() (东方财富)。
    """
    try:
        import akshare as ak
        df = ak.stock_zh_a_spot_em()
    except Exception as e:
        logger.error(f"获取行情数据失败: {e}")
        return 0

    from backend.database.models import StockSpot

    count = 0
    now = _now_str()
    for _, row in df.iterrows():
        code = str(row.get("代码", "")).strip()
        if not code:
            continue
        spot = session.query(StockSpot).filter_by(code=code).first()
        price = _safe_float(row.get("最新价"))
        change_pct = _safe_float(row.get("涨跌幅"))
        if price is None or change_pct is None:
            continue

        if spot:
            spot.name = str(row.get("名称", spot.name))
            spot.current_price = price
            spot.change_pct = change_pct
            spot.change_amount = _safe_float(row.get("涨跌额"))
            spot.volume = _safe_float(row.get("成交量"))
            spot.turnover = _safe_float(row.get("成交额"))
            spot.turnover_rate = _safe_float(row.get("换手率"))
            spot.amplitude = _safe_float(row.get("振幅"))
            spot.high = _safe_float(row.get("最高"))
            spot.low = _safe_float(row.get("最低"))
            spot.open = _safe_float(row.get("今开"))
            spot.prev_close = _safe_float(row.get("昨收"))
            spot.pe_ttm = _safe_float(row.get("市盈率-动态"))
            spot.pb = _safe_float(row.get("市净率"))
            spot.fetched_at = now
        else:
            session.add(StockSpot(
                code=code,
                name=str(row.get("名称", "")),
                current_price=price,
                change_pct=change_pct,
                change_amount=_safe_float(row.get("涨跌额")),
                volume=_safe_float(row.get("成交量")),
                turnover=_safe_float(row.get("成交额")),
                turnover_rate=_safe_float(row.get("换手率")),
                amplitude=_safe_float(row.get("振幅")),
                high=_safe_float(row.get("最高")),
                low=_safe_float(row.get("最低")),
                open=_safe_float(row.get("今开")),
                prev_close=_safe_float(row.get("昨收")),
                pe_ttm=_safe_float(row.get("市盈率-动态")),
                pb=_safe_float(row.get("市净率")),
                fetched_at=now,
            ))
        count += 1

    session.commit()
    logger.info(f"行情数据已更新: {count} 只")
    return count


# ========== 日K线 ==========

def fetch_daily_kline(code: str, period: str = "daily", days: int = 250, session=None):
    """
    拉取单只股票的日K线数据。
    使用 akshare stock_zh_a_hist()。
    """
    try:
        import akshare as ak
        df = ak.stock_zh_a_hist(
            symbol=code,
            period=period,
            start_date=(datetime.now().date() - pd.Timedelta(days=days)).strftime("%Y%m%d"),
            end_date=datetime.now().strftime("%Y%m%d"),
            adjust="qfq",  # 前复权
        )
    except Exception as e:
        logger.error(f"获取 {code} K线失败: {e}")
        return 0

    from backend.database.models import StockDaily

    count = 0
    for _, row in df.iterrows():
        date_str = str(row.get("日期", ""))[:10]
        if not date_str:
            continue
        existing = session.query(StockDaily).filter_by(code=code, trade_date=date_str).first()
        if existing:
            existing.open = _safe_float(row.get("开盘"))
            existing.high = _safe_float(row.get("最高"))
            existing.low = _safe_float(row.get("最低"))
            existing.close = _safe_float(row.get("收盘"))
            existing.volume = _safe_float(row.get("成交量"))
            existing.turnover = _safe_float(row.get("成交额"))
            existing.change_pct = _safe_float(row.get("涨跌幅"))
        else:
            session.add(StockDaily(
                code=code,
                trade_date=date_str,
                open=_safe_float(row.get("开盘")),
                high=_safe_float(row.get("最高")),
                low=_safe_float(row.get("最低")),
                close=_safe_float(row.get("收盘")),
                volume=_safe_float(row.get("成交量")),
                turnover=_safe_float(row.get("成交额")),
                change_pct=_safe_float(row.get("涨跌幅")),
            ))
        count += 1

    session.commit()
    return count


# ========== 分时数据 ==========

def fetch_intraday(code: str, period: str = "1", session=None):
    """
    拉取单只股票当日分时数据。
    使用 akshare stock_zh_a_minute()。
    period: '1'=1分钟, '5'=5分钟, '15'=15分钟
    """
    try:
        import akshare as ak
        symbol = code
        df = ak.stock_zh_a_minute(symbol=symbol, period=period, adjust="")
    except Exception as e:
        logger.error(f"获取 {code} 分时数据失败: {e}")
        return []

    from backend.database.models import StockIntraday

    records = []
    now = _now_str()
    for _, row in df.iterrows():
        time_str = str(row.get("时间", row.get("day", "")))
        price = _safe_float(row.get("收盘", row.get("close")))
        volume = _safe_float(row.get("成交量", row.get("volume")))
        if not time_str or price is None:
            continue
        records.append({
            "time": time_str,
            "price": price,
            "avg_price": _safe_float(row.get("均价", price)),
            "volume": volume or 0,
            "turnover": _safe_float(row.get("成交额", 0)) or 0,
        })

    # 写入DB
    for r in records:
        existing = session.query(StockIntraday).filter_by(code=code, time=r["time"]).first()
        if not existing:
            session.add(StockIntraday(
                code=code, time=r["time"],
                price=r["price"], avg_price=r["avg_price"],
                volume=r["volume"], turnover=r["turnover"],
                fetched_at=now,
            ))
    session.commit()
    logger.info(f"{code} 分时数据: {len(records)} 条")
    return records


# ========== 盘口五档 ==========

def fetch_depth(code: str, session=None):
    """
    拉取单只股票盘口五档行情。
    使用 akshare stock_bid_ask_em()。
    """
    try:
        import akshare as ak
        df = ak.stock_bid_ask_em(symbol=code)
    except Exception as e:
        logger.error(f"获取 {code} 盘口数据失败: {e}")
        return None

    from backend.database.models import StockDepth

    if df.empty:
        return None

    now = _now_str()
    try:
        row = df.iloc[0]
        ask_prices = []
        ask_vols = []
        bid_prices = []
        bid_vols = []
        for i in range(1, 6):
            ask_prices.append(_safe_float(row.get(f"卖{i}", row.get(f"ask{i}"))))
            ask_vols.append(_safe_float(row.get(f"卖{i}量", row.get(f"ask{i}_vol"))))
            bid_prices.append(_safe_float(row.get(f"买{i}", row.get(f"bid{i}"))))
            bid_vols.append(_safe_float(row.get(f"买{i}量", row.get(f"bid{i}_vol"))))

        existing = session.query(StockDepth).filter_by(code=code).first()
        if existing:
            for i in range(5):
                setattr(existing, f"ask{i+1}", ask_prices[i])
                setattr(existing, f"ask{i+1}_vol", ask_vols[i])
                setattr(existing, f"bid{i+1}", bid_prices[i])
                setattr(existing, f"bid{i+1}_vol", bid_vols[i])
            existing.fetched_at = now
        else:
            session.add(StockDepth(
                code=code,
                ask5=ask_prices[4], ask5_vol=ask_vols[4],
                ask4=ask_prices[3], ask4_vol=ask_vols[3],
                ask3=ask_prices[2], ask3_vol=ask_vols[2],
                ask2=ask_prices[1], ask2_vol=ask_vols[1],
                ask1=ask_prices[0], ask1_vol=ask_vols[0],
                bid1=bid_prices[0], bid1_vol=bid_vols[0],
                bid2=bid_prices[1], bid2_vol=bid_vols[1],
                bid3=bid_prices[2], bid3_vol=bid_vols[2],
                bid4=bid_prices[3], bid4_vol=bid_vols[3],
                bid5=bid_prices[4], bid5_vol=bid_vols[4],
                fetched_at=now,
            ))
        session.commit()
    except Exception as e:
        logger.error(f"解析 {code} 盘口数据失败: {e}")
        return None

    return {
        "code": code,
        "asks": [{"price": ask_prices[i], "volume": ask_vols[i]} for i in range(5)],
        "bids": [{"price": bid_prices[i], "volume": bid_vols[i]} for i in range(5)],
        "fetched_at": now,
    }


# ========== 批量K线（多只股票） ==========

def fetch_batch_kline(codes: list[str], days: int = 250, session=None):
    """批量拉取多只股票的日K线"""
    count = 0
    for i, code in enumerate(codes):
        try:
            n = fetch_daily_kline(code=code, days=days, session=session)
            count += n
            if i < len(codes) - 1:
                from backend.config import AKSHARE_RATE_LIMIT
                import time
                time.sleep(AKSHARE_RATE_LIMIT)
        except Exception as e:
            logger.error(f"批量K线 {code} 失败: {e}")
    return count

def fetch_financials(code: str, session=None):
    """
    拉取单只股票的财务指标。
    使用 akshare stock_financial_analysis_indicator()。
    """
    try:
        import akshare as ak
        df = ak.stock_financial_analysis_indicator(symbol=code)
    except Exception as e:
        logger.error(f"获取 {code} 财务数据失败: {e}")
        return 0

    from backend.database.models import StockFinancial

    if df.empty:
        return 0

    count = 0
    # 取最近4个季度
    for _, row in df.head(4).iterrows():
        period = str(row.get("日期", ""))[:7]  # e.g. "2025-03" -> 简化为 "2025Q1"
        if not period:
            continue
        # 转为季度格式
        try:
            y, m = period.split("-")
            q = str((int(m) - 1) // 3 + 1)
            report_period = f"{y}Q{q}"
        except ValueError:
            report_period = period

        existing = session.query(StockFinancial).filter_by(code=code, report_period=report_period).first()
        vals = {
            "roe": _safe_float(row.get("净资产收益率")),
            "gross_margin": _safe_float(row.get("销售毛利率")),
            "net_margin": _safe_float(row.get("销售净利率")),
            "revenue_yoy": _safe_float(row.get("营业收入同比增长")),
            "profit_yoy": _safe_float(row.get("净利润同比增长")),
            "eps": _safe_float(row.get("基本每股收益")),
            "bvps": _safe_float(row.get("每股净资产")),
            "debt_ratio": _safe_float(row.get("资产负债率")),
            "current_ratio": _safe_float(row.get("流动比率")),
            "quick_ratio": _safe_float(row.get("速动比率")),
            "op_cash_flow": _safe_float(row.get("经营现金净流量")),
            "fetched_at": _now_str(),
        }
        if existing:
            for k, v in vals.items():
                if v is not None:
                    setattr(existing, k, v)
        else:
            session.add(StockFinancial(code=code, report_period=report_period, **vals))
        count += 1

    session.commit()
    return count


# ========== 演示模式数据 ==========

def seed_demo_data(session, n_stocks: int = 500):
    """
    离线演示：为已有股票生成模拟行情 + 财务数据。
    当 akshare 无法连接时使用。
    """
    import numpy as np
    from backend.database.models import StockUniverse, StockSpot, StockFinancial, StockFactor, StockDaily, StockIntraday

    rng = np.random.default_rng(42)
    now = _now_str()

    stocks = session.query(StockUniverse).filter(StockUniverse.is_st == 0).limit(n_stocks).all()
    if not stocks:
        logger.warning("无股票基础数据，请先执行 fetch_stock_universe")
        return 0

    # 清除旧的模拟数据
    session.query(StockSpot).delete()
    session.query(StockFinancial).delete()
    session.query(StockFactor).delete()
    session.query(StockDaily).delete()
    session.query(StockIntraday).delete()

    count = 0
    for stock in stocks:
        code = stock.code
        # 生成合理的随机价格和财务数据
        base_price = float(rng.uniform(5, 200))
        change_pct = float(rng.normal(0, 2.5))
        pe = float(max(5, min(300, rng.lognormal(3.2, 0.7))))  # PE ~ 5-300
        pb = float(max(0.5, min(20, rng.lognormal(0.8, 0.6))))  # PB ~ 0.5-20
        roe = float(rng.normal(10, 15))  # ROE ~ -20 to 40
        gross_margin = float(min(95, max(5, rng.normal(30, 18))))
        net_margin = float(min(60, max(-10, rng.normal(12, 10))))
        revenue_yoy = float(rng.normal(15, 25))
        profit_yoy = float(rng.normal(12, 30))

        session.add(StockSpot(
            code=code, name=stock.name,
            current_price=round(base_price, 2),
            change_pct=round(change_pct, 2),
            change_amount=round(base_price * change_pct / 100, 2),
            volume=float(rng.uniform(1e4, 5e7)),
            turnover=float(rng.uniform(1e6, 5e9)),
            turnover_rate=float(rng.uniform(0.5, 15)),
            amplitude=float(rng.uniform(1, 10)),
            high=round(base_price * (1 + abs(rng.normal(0, 0.03))), 2),
            low=round(base_price * (1 - abs(rng.normal(0, 0.03))), 2),
            open=round(base_price * (1 + rng.normal(0, 0.01)), 2),
            prev_close=round(base_price * (1 - change_pct / 100), 2),
            pe_ttm=round(pe, 2),
            pb=round(pb, 2),
            fetched_at=now,
        ))

        # 最近4个季度财务数据
        for q_offset in range(4):
            q = 4 - q_offset
            y = 2026 if q_offset < 2 else 2025
            report_period = f"{y}Q{q}"
            session.add(StockFinancial(
                code=code, report_period=report_period,
                roe=round(float(rng.normal(roe, 5)), 2),
                gross_margin=round(float(rng.normal(gross_margin, 3)), 2),
                net_margin=round(float(rng.normal(net_margin, 3)), 2),
                revenue_yoy=round(float(rng.normal(revenue_yoy, 10)), 2),
                profit_yoy=round(float(rng.normal(profit_yoy, 12)), 2),
                eps=round(float(max(0.01, rng.lognormal(0.3, 0.8))), 3),
                bvps=round(float(max(1, rng.lognormal(2, 0.5))), 2),
                debt_ratio=round(float(min(90, max(5, rng.normal(45, 20)))), 2),
                current_ratio=round(float(max(0.3, rng.lognormal(0.5, 0.5))), 2),
                quick_ratio=round(float(max(0.2, rng.lognormal(0.3, 0.5))), 2),
                op_cash_flow=round(float(rng.lognormal(0.5, 1.5)), 2),
                fetched_at=now,
            ))

        # 生成演示K线数据（最近120天）
        from datetime import datetime as dt, timedelta
        kline_base = base_price
        for days_ago in range(120, 0, -1):
            trade_date = (dt.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            daily_chg = float(rng.normal(0, 0.02))
            kline_base *= (1 + daily_chg * 0.3)  # 缓慢漂移
            k_open = round(kline_base * (1 + rng.normal(0, 0.005)), 2)
            k_close = round(kline_base * (1 + rng.normal(0, 0.005)), 2)
            k_high = round(max(k_open, k_close) * (1 + abs(rng.normal(0, 0.01))), 2)
            k_low = round(min(k_open, k_close) * (1 - abs(rng.normal(0, 0.01))), 2)
            session.add(StockDaily(
                code=code, trade_date=trade_date,
                open=k_open, high=k_high, low=k_low, close=k_close,
                volume=float(rng.uniform(1e4, 5e7)),
                turnover=float(rng.uniform(1e6, 5e9)),
                change_pct=round((k_close - k_open) / k_open * 100, 2),
            ))

        # 生成演示分时数据（当日240分钟）
        intra_base = base_price
        for minute in range(0, 240):
            t = f"09:{(30+minute)//60:02d}:{(30+minute)%60:02d}" if minute < 120 else f"{(13+(minute-120)//60):02d}:{(minute-120)%60:02d}:00"
            time_str = f"{dt.now().strftime('%Y-%m-%d')} {t}"
            intra_base *= (1 + rng.normal(0, 0.0008))
            session.add(StockIntraday(
                code=code, time=time_str,
                price=round(intra_base, 2),
                avg_price=round(intra_base * (1 + rng.normal(0, 0.0005)), 2),
                volume=float(rng.uniform(100, 50000)),
                turnover=float(rng.uniform(1e4, 5e7)),
                fetched_at=now,
            ))

        count += 1

    session.commit()
    logger.info(f"演示数据生成完成: {count} 只股票（含行情+4期财务+120日K线+分时）")
    return count


# ========== 批量初始化 ==========

def seed_data(session, demo_mode: bool = False):
    """首次运行：拉取股票列表 + 行情快照。demo_mode=True 使用模拟数据。"""
    logger.info("开始初始化数据...")
    n_stocks = fetch_stock_universe(session)
    if n_stocks == 0:
        logger.warning("股票列表获取失败，请检查网络或akshare配置")
        return

    if demo_mode:
        seed_demo_data(session, n_stocks=500)
        return

    n_spot = fetch_spot_data(session)
    if n_spot == 0:
        logger.warning("行情数据获取失败，切换到演示模式...")
        seed_demo_data(session, n_stocks=500)
    else:
        logger.info(f"数据初始化完成: {n_stocks} 只股票, {n_spot} 条行情")
