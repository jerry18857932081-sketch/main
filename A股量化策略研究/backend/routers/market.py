"""市场概况路由"""
import logging
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.schemas.schemas import MarketOverview, MarketIndex, SectorHeatItem

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/indices", response_model=MarketOverview)
def get_indices(db: Session = Depends(get_db)):
    """
    获取四大指数实时行情。
    当前使用 akshare 的 stock_zh_index_spot_em()，失败时返回模拟数据。
    """
    indices = []
    try:
        import akshare as ak
        df = ak.stock_zh_index_spot_em()
        # 筛选四大指数
        target_codes = {"上证指数", "深证成指", "创业板指", "科创50"}
        for _, row in df.iterrows():
            name = str(row.get("名称", ""))
            if name in target_codes:
                indices.append(MarketIndex(
                    code=str(row.get("代码", "")),
                    name=name,
                    current=float(row.get("最新价", 0) or 0),
                    change_pct=float(row.get("涨跌幅", 0) or 0),
                    change_amount=float(row.get("涨跌额", 0) or 0),
                    volume=float(row.get("成交量", 0) or 0),
                    turnover=float(row.get("成交额", 0) or 0),
                ))
    except Exception as e:
        logger.warning(f"获取指数失败，使用模拟数据: {e}")
        indices = _mock_indices()

    if not indices:
        indices = _mock_indices()

    return MarketOverview(
        indices=indices,
        update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )


def _mock_indices():
    """离线模拟数据"""
    return [
        MarketIndex(code="000001", name="上证指数", current=3350.0, change_pct=0.32, change_amount=10.7),
        MarketIndex(code="399001", name="深证成指", current=10850.0, change_pct=-0.15, change_amount=-16.3),
        MarketIndex(code="399006", name="创业板指", current=2180.0, change_pct=0.58, change_amount=12.6),
        MarketIndex(code="000688", name="科创50", current=960.0, change_pct=1.20, change_amount=11.4),
    ]


@router.get("/sectors/heatmap")
def get_sector_heatmap(db: Session = Depends(get_db)):
    """
    获取行业板块涨跌热力图。
    使用 akshare stock_board_industry_name_em()。
    """
    try:
        import akshare as ak
        df = ak.stock_board_industry_name_em()
        items = []
        for _, row in df.head(30).iterrows():
            items.append(SectorHeatItem(
                name=str(row.get("板块名称", "")),
                change_pct=float(row.get("涨跌幅", 0) or 0),
                leading_stock=str(row.get("领涨股票", "")) if row.get("领涨股票") else None,
            ).model_dump())
        return items
    except Exception as e:
        logger.warning(f"获取板块热力图失败: {e}")
        return []
