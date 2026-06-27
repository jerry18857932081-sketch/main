"""股票数据路由"""
import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.database.models import StockUniverse, StockSpot, StockFinancial, StockDaily, StockFactor, StockIntraday, StockDepth
from backend.services.data_pipeline import fetch_intraday, fetch_depth, fetch_daily_kline
from backend.schemas.schemas import StockSummary, StockListResponse, StockDetail, KlineItem, KlineResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("", response_model=StockListResponse)
def list_stocks(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    industry: str = Query(None, description="申万一级行业"),
    sort_by: str = Query("change_pct", description="排序字段"),
    order: str = Query("desc", description="asc/desc"),
    db: Session = Depends(get_db),
):
    """分页获取股票列表（含行情概要）"""
    # Join stock_spot 获取行情
    query = db.query(StockUniverse, StockSpot).outerjoin(
        StockSpot, StockUniverse.code == StockSpot.code
    )

    if industry:
        query = query.filter(StockUniverse.industry_l1 == industry)

    # 排除ST
    query = query.filter(StockUniverse.is_st == 0)

    # 排序
    if sort_by == "change_pct":
        order_col = StockSpot.change_pct
    elif sort_by == "pe_ttm":
        order_col = StockSpot.pe_ttm
    elif sort_by == "market_cap":
        order_col = StockUniverse.market_cap
    else:
        order_col = StockSpot.current_price

    if order_col is not None:
        if order == "asc":
            query = query.order_by(order_col.asc().nullslast())
        else:
            query = query.order_by(order_col.desc().nullslast())

    total = query.count()
    offset = (page - 1) * page_size
    rows = query.offset(offset).limit(page_size).all()

    data = []
    for uni, spot in rows:
        data.append(StockSummary(
            code=uni.code,
            name=uni.name,
            industry_l1=uni.industry_l1,
            current_price=spot.current_price if spot else None,
            change_pct=spot.change_pct if spot else None,
            pe_ttm=spot.pe_ttm if spot else None,
            pb=spot.pb if spot else None,
            market_cap=uni.market_cap,
        ))

    return StockListResponse(total=total, page=page, page_size=page_size, data=data)


@router.get("/search")
def search_stocks(q: str = Query("", min_length=1), db: Session = Depends(get_db)):
    """按名称/代码搜索股票（最多20条）"""
    results = db.query(StockUniverse).filter(
        (StockUniverse.name.contains(q)) | (StockUniverse.code.contains(q))
    ).limit(20).all()

    return [
        {"code": s.code, "name": s.name, "industry_l1": s.industry_l1}
        for s in results
    ]


@router.get("/{code}")
def get_stock_detail(code: str, db: Session = Depends(get_db)):
    """获取个股详情：基础信息 + 行情 + 最新财务 + 因子分"""
    uni = db.query(StockUniverse).filter_by(code=code).first()
    if not uni:
        raise HTTPException(status_code=404, detail="股票不存在")

    spot = db.query(StockSpot).filter_by(code=code).first()
    fin = db.query(StockFinancial).filter_by(code=code).order_by(
        StockFinancial.report_period.desc()
    ).first()
    factors = db.query(StockFactor).filter_by(code=code).order_by(
        StockFactor.calc_date.desc()
    ).limit(20).all()

    return {
        "code": uni.code,
        "name": uni.name,
        "industry_l1": uni.industry_l1,
        "industry_l2": uni.industry_l2,
        "market_cap": uni.market_cap,
        "spot": {
            "current_price": spot.current_price if spot else None,
            "change_pct": spot.change_pct if spot else None,
            "change_amount": spot.change_amount if spot else None,
            "volume": spot.volume if spot else None,
            "turnover": spot.turnover if spot else None,
            "turnover_rate": spot.turnover_rate if spot else None,
            "amplitude": spot.amplitude if spot else None,
            "high": spot.high if spot else None,
            "low": spot.low if spot else None,
            "open": spot.open if spot else None,
            "prev_close": spot.prev_close if spot else None,
            "pe_ttm": spot.pe_ttm if spot else None,
            "pb": spot.pb if spot else None,
        } if spot else None,
        "fundamentals": [
            {
                "period": fin.report_period,
                "roe": fin.roe,
                "gross_margin": fin.gross_margin,
                "net_margin": fin.net_margin,
                "revenue_yoy": fin.revenue_yoy,
                "profit_yoy": fin.profit_yoy,
                "eps": fin.eps,
                "bvps": fin.bvps,
                "debt_ratio": fin.debt_ratio,
                "current_ratio": fin.current_ratio,
                "op_cash_flow": fin.op_cash_flow,
            }
        ] if fin else [],
        "factors": [
            {
                "dimension": f.dimension,
                "factor_name": f.factor_name,
                "raw_value": f.raw_value,
                "z_score": f.z_score,
                "percentile": f.percentile,
                "score": f.score,
            }
            for f in factors
        ],
    }


@router.get("/{code}/kline", response_model=KlineResponse)
def get_stock_kline(
    code: str,
    period: str = Query("daily", description="daily/weekly/monthly/30min"),
    limit: int = Query(120, description="返回条数"),
    db: Session = Depends(get_db),
):
    """获取个股K线数据，支持日/周/月/30分钟"""
    uni = db.query(StockUniverse).filter_by(code=code).first()
    if not uni:
        raise HTTPException(status_code=404, detail="股票不存在")

    # 取足够多的日线数据用于聚合
    fetch_limit = limit * 10 if period != "daily" else limit
    records = db.query(StockDaily).filter_by(code=code).order_by(
        StockDaily.trade_date.desc()
    ).limit(fetch_limit).all()
    records.reverse()  # 升序

    if not records:
        return KlineResponse(code=code, name=uni.name, klines=[])

    if period == "daily":
        klines = [_to_kline(r) for r in records[-limit:]]
    elif period == "weekly":
        klines = _aggregate_kline(records, "W", limit)
    elif period == "monthly":
        klines = _aggregate_kline(records, "M", limit)
    elif period == "30min":
        # 30分钟线从intraday表或实时拉取
        klines = _get_30min_kline(code, limit, db)
    else:
        klines = [_to_kline(r) for r in records[-limit:]]

    return KlineResponse(code=code, name=uni.name, klines=klines)


def _to_kline(r):
    return KlineItem(date=r.trade_date, open=r.open or 0, close=r.close or 0,
                     high=r.high or 0, low=r.low or 0, volume=r.volume or 0)


def _aggregate_kline(daily_records, freq, limit):
    """从日线聚合为周线/月线"""
    import pandas as pd
    df = pd.DataFrame([{
        'date': r.trade_date, 'open': r.open, 'close': r.close,
        'high': r.high, 'low': r.low, 'volume': r.volume
    } for r in daily_records])
    if df.empty:
        return []
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')

    grouped = df.resample(freq).agg({
        'open': 'first', 'close': 'last',
        'high': 'max', 'low': 'min',
        'volume': 'sum'
    }).dropna()

    result = []
    for idx, row in grouped.tail(limit).iterrows():
        result.append(KlineItem(
            date=idx.strftime('%Y-%m-%d'),
            open=round(row['open'], 2), close=round(row['close'], 2),
            high=round(row['high'], 2), low=round(row['low'], 2),
            volume=row['volume'],
        ))
    return result


def _get_30min_kline(code, limit, db):
    """获取30分钟K线（从intraday聚合）"""
    records = db.query(StockIntraday).filter_by(code=code).order_by(
        StockIntraday.time.asc()
    ).all()
    if not records:
        return []

    # 按30分钟桶聚合
    import pandas as pd
    df = pd.DataFrame([{
        'time': r.time, 'price': r.price, 'volume': r.volume
    } for r in records])
    if df.empty:
        return []
    df['time'] = pd.to_datetime(df['time'])
    df = df.set_index('time')

    grouped = df.resample('30T').agg({
        'price': ['first', 'last', 'max', 'min'],
        'volume': 'sum'
    }).dropna()

    result = []
    for idx, row in grouped.tail(limit).iterrows():
        result.append(KlineItem(
            date=idx.strftime('%H:%M'),
            open=round(row[('price','first')], 2),
            close=round(row[('price','last')], 2),
            high=round(row[('price','max')], 2),
            low=round(row[('price','min')], 2),
            volume=row[('volume','sum')],
        ))
    return result


@router.get("/{code}/intraday")
def get_stock_intraday(code: str, db: Session = Depends(get_db)):
    """获取个股分时数据（当日分钟线）"""
    uni = db.query(StockUniverse).filter_by(code=code).first()
    if not uni:
        raise HTTPException(status_code=404, detail="股票不存在")

    records = db.query(StockIntraday).filter_by(code=code).order_by(StockIntraday.time.asc()).all()

    if not records:
        # 尝试实时拉取
        records_raw = fetch_intraday(code=code, period="1", session=db)
        if not records_raw:
            return {"code": code, "name": uni.name, "intraday": [], "note": "暂无分时数据"}
        return {"code": code, "name": uni.name, "intraday": records_raw}

    return {
        "code": code,
        "name": uni.name,
        "intraday": [{
            "time": r.time,
            "price": r.price,
            "avg_price": r.avg_price,
            "volume": r.volume,
            "turnover": r.turnover,
        } for r in records],
    }


@router.get("/{code}/depth")
def get_stock_depth(code: str, refresh: bool = Query(False), db: Session = Depends(get_db)):
    """获取个股盘口五档行情。refresh=true 强制实时拉取"""
    uni = db.query(StockUniverse).filter_by(code=code).first()
    if not uni:
        raise HTTPException(status_code=404, detail="股票不存在")

    depth = db.query(StockDepth).filter_by(code=code).first()

    if refresh or not depth:
        result = fetch_depth(code=code, session=db)
        if result:
            return {"code": code, "name": uni.name, **result}
        if depth:
            # 拉取失败但DB有历史数据
            pass
        else:
            return {"code": code, "name": uni.name, "asks": [], "bids": [], "note": "暂无盘口数据"}

    # 返回DB缓存
    return {
        "code": code,
        "name": uni.name,
        "asks": [
            {"price": depth.ask1, "volume": depth.ask1_vol},
            {"price": depth.ask2, "volume": depth.ask2_vol},
            {"price": depth.ask3, "volume": depth.ask3_vol},
            {"price": depth.ask4, "volume": depth.ask4_vol},
            {"price": depth.ask5, "volume": depth.ask5_vol},
        ],
        "bids": [
            {"price": depth.bid1, "volume": depth.bid1_vol},
            {"price": depth.bid2, "volume": depth.bid2_vol},
            {"price": depth.bid3, "volume": depth.bid3_vol},
            {"price": depth.bid4, "volume": depth.bid4_vol},
            {"price": depth.bid5, "volume": depth.bid5_vol},
        ],
        "fetched_at": depth.fetched_at,
    }


@router.get("/{code}/live")
def get_stock_live(code: str, refresh: bool = Query(True), db: Session = Depends(get_db)):
    """
    个股实时数据聚合：
    - 最新行情
    - 最近60条分时线
    - 盘口五档
    - 最近120日K线（精简版）
    前端轮询用此端点，一次请求获取全部实时数据。
    """
    uni = db.query(StockUniverse).filter_by(code=code).first()
    if not uni:
        raise HTTPException(status_code=404, detail="股票不存在")

    # 行情
    spot = db.query(StockSpot).filter_by(code=code).first()

    # 分时
    intraday_rows = db.query(StockIntraday).filter_by(code=code).order_by(
        StockIntraday.time.desc()
    ).limit(60).all()
    intraday = [{"time": i.time, "price": i.price, "avg_price": i.avg_price,
                  "volume": i.volume, "turnover": i.turnover} for i in reversed(intraday_rows)]

    # 盘口
    depth = db.query(StockDepth).filter_by(code=code).first()
    depth_data = None
    if depth:
        depth_data = {
            "asks": [{"price": depth.ask1, "volume": depth.ask1_vol},
                     {"price": depth.ask2, "volume": depth.ask2_vol},
                     {"price": depth.ask3, "volume": depth.ask3_vol}],
            "bids": [{"price": depth.bid1, "volume": depth.bid1_vol},
                     {"price": depth.bid2, "volume": depth.bid2_vol},
                     {"price": depth.bid3, "volume": depth.bid3_vol}],
        }

    # K线精简（最近60日）
    klines_rows = db.query(StockDaily).filter_by(code=code).order_by(
        StockDaily.trade_date.desc()
    ).limit(60).all()
    klines = [{"date": k.trade_date, "open": k.open, "close": k.close,
                "high": k.high, "low": k.low, "volume": k.volume} for k in reversed(klines_rows)]

    return {
        "code": code,
        "name": uni.name,
        "spot": {
            "current_price": spot.current_price if spot else None,
            "change_pct": spot.change_pct if spot else None,
            "open": spot.open if spot else None,
            "high": spot.high if spot else None,
            "low": spot.low if spot else None,
            "prev_close": spot.prev_close if spot else None,
            "volume": spot.volume if spot else None,
            "turnover": spot.turnover if spot else None,
            "turnover_rate": spot.turnover_rate if spot else None,
            "pe_ttm": spot.pe_ttm if spot else None,
            "pb": spot.pb if spot else None,
            "fetched_at": spot.fetched_at if spot else None,
        } if spot else None,
        "intraday": intraday,
        "depth": depth_data,
        "klines": klines,
    }
