"""Pydantic 请求/响应模型"""
from pydantic import BaseModel, Field
from typing import Optional


# ========== 市场相关 ==========
class MarketIndex(BaseModel):
    code: str
    name: str
    current: float
    change_pct: float
    change_amount: float
    volume: Optional[float] = None
    turnover: Optional[float] = None

class MarketOverview(BaseModel):
    indices: list[MarketIndex]
    update_time: str

class SectorHeatItem(BaseModel):
    name: str
    change_pct: float
    leading_stock: Optional[str] = None
    fund_flow: Optional[float] = None  # 主力净流入(亿)


# ========== 股票相关 ==========
class StockSummary(BaseModel):
    code: str
    name: str
    industry_l1: Optional[str] = None
    current_price: Optional[float] = None
    change_pct: Optional[float] = None
    pe_ttm: Optional[float] = None
    pb: Optional[float] = None
    market_cap: Optional[float] = None

class StockListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    data: list[StockSummary]

class FactorItem(BaseModel):
    dimension: str
    factor_name: str
    display_name: str
    raw_value: float
    z_score: float
    percentile: float
    score: float

class StockDetail(BaseModel):
    code: str
    name: str
    industry_l1: Optional[str] = None
    industry_l2: Optional[str] = None
    market_cap: Optional[float] = None
    spot: Optional[dict] = None
    fundamentals: Optional[list[dict]] = None
    factors: Optional[list[FactorItem]] = None

class KlineItem(BaseModel):
    date: str
    open: float
    close: float
    high: float
    low: float
    volume: float

class KlineResponse(BaseModel):
    code: str
    name: str
    klines: list[KlineItem]


# ========== 筛选相关 ==========
class FactorMeta(BaseModel):
    """因子元数据（前端展示用）"""
    dimension: str
    dimension_name: str
    factor_name: str
    display_name: str
    description: str
    direction: str  # 'higher_better' | 'lower_better'
    default_weight: float

class ScreenFilter(BaseModel):
    factor: str
    min: Optional[float] = None
    max: Optional[float] = None

class ScreenRequest(BaseModel):
    filters: list[ScreenFilter] = []
    dimension_weights: dict[str, float] = Field(
        default_factory=lambda: {
            "performance": 25,
            "valuation": 20,
            "growth": 25,
            "trend": 15,
            "business": 15,
        }
    )
    sector: Optional[str] = None          # 申万一级行业，None=全市场
    universe: str = "all"                 # 'all' | 'main' | 'gem' | 'star'
    limit: int = 50
    sort_by: str = "total_score"          # 'total_score' | dimension name
    order: str = "desc"

class ScreenResultItem(BaseModel):
    rank: int
    code: str
    name: str
    industry_l1: Optional[str] = None
    current_price: Optional[float] = None
    change_pct: Optional[float] = None
    pe_ttm: Optional[float] = None
    pb: Optional[float] = None
    roe: Optional[float] = None
    total_score: float
    dimension_scores: dict[str, float]   # e.g. {"performance": 72.5, ...}
    factor_scores: dict[str, float]      # e.g. {"roe": 1.2, "pe_ttm": 0.8, ...}

class ScreenResponse(BaseModel):
    total_matched: int
    results: list[ScreenResultItem]
    meta: dict = Field(default_factory=lambda: {
        "factor_count": 0,
        "universe_size": 0,
        "filters_applied": 0,
    })

class ScreenTemplateSave(BaseModel):
    name: str
    description: Optional[str] = None
    filters: list[ScreenFilter]
    weights: dict[str, float]

class ScreenTemplateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: str


# ========== 买点相关 ==========
class TimingSignalItem(BaseModel):
    code: str
    name: str
    signal_type: str                       # 'oversold' | 'breakout'
    signal_date: str
    signal_score: float                    # 0-100
    current_price: Optional[float] = None
    change_pct: Optional[float] = None
    details: dict = Field(default_factory=dict)  # 信号详情


# ========== 赛道相关 ==========
class SectorChainSave(BaseModel):
    event_name: str
    chain_json: str                        # JSON string of nodes + edges
    mapped_sectors: Optional[list[str]] = None


class SectorChainResponse(BaseModel):
    id: int
    event_name: str
    chain_json: str
    mapped_sectors: Optional[list[str]] = None
    created_at: str
