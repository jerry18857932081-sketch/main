"""SQLAlchemy ORM 模型"""
from sqlalchemy import Column, String, Float, Integer, Text, create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class StockUniverse(Base):
    """股票基础信息"""
    __tablename__ = "stock_universe"

    code = Column(String(6), primary_key=True)     # 股票代码 如 '300308'
    name = Column(String(50), nullable=False)       # 股票名称
    exchange = Column(String(2))                    # 交易所 'SH'/'SZ'/'BJ'
    industry_l1 = Column(String(50))                # 申万一级行业
    industry_l2 = Column(String(50))                # 申万二级行业
    market_cap = Column(Float)                      # 总市值（亿元）
    circulating_cap = Column(Float)                 # 流通市值（亿元）
    list_date = Column(String(10))                  # 上市日期
    is_st = Column(Integer, default=0)              # 是否ST
    updated_at = Column(String(20))


class StockSpot(Base):
    """实时行情快照"""
    __tablename__ = "stock_spot"

    code = Column(String(6), primary_key=True)
    name = Column(String(50))
    current_price = Column(Float)
    change_pct = Column(Float)                      # 涨跌幅(%)
    change_amount = Column(Float)                   # 涨跌额
    volume = Column(Float)                          # 成交量(手)
    turnover = Column(Float)                        # 成交额(元)
    turnover_rate = Column(Float)                   # 换手率(%)
    amplitude = Column(Float)                       # 振幅(%)
    high = Column(Float)
    low = Column(Float)
    open = Column(Float)
    prev_close = Column(Float)
    pe_ttm = Column(Float)                          # 市盈率(TTM)
    pb = Column(Float)                              # 市净率
    fetched_at = Column(String(20))


class StockFinancial(Base):
    """财务指标（季度）"""
    __tablename__ = "stock_financials"

    code = Column(String(6), primary_key=True)
    report_period = Column(String(10), primary_key=True)  # e.g. '2025Q3'
    roe = Column(Float)                              # ROE (%)
    gross_margin = Column(Float)                     # 毛利率 (%)
    net_margin = Column(Float)                       # 净利率 (%)
    revenue_yoy = Column(Float)                      # 营收同比增速 (%)
    profit_yoy = Column(Float)                       # 利润同比增速 (%)
    eps = Column(Float)                              # 每股收益
    bvps = Column(Float)                             # 每股净资产
    debt_ratio = Column(Float)                       # 资产负债率 (%)
    current_ratio = Column(Float)                    # 流动比率
    quick_ratio = Column(Float)                      # 速动比率
    op_cash_flow = Column(Float)                     # 经营活动现金流（亿元）
    dividend_yield = Column(Float)                   # 股息率 (%)
    fetched_at = Column(String(20))


class StockDaily(Base):
    """日K线"""
    __tablename__ = "stock_daily"

    code = Column(String(6), primary_key=True)
    trade_date = Column(String(10), primary_key=True)  # YYYY-MM-DD
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)                           # 成交量(手)
    turnover = Column(Float)                         # 成交额(元)
    change_pct = Column(Float)                       # 涨跌幅(%)


class StockFactor(Base):
    """五维因子分"""
    __tablename__ = "stock_factors"

    code = Column(String(6), primary_key=True)
    calc_date = Column(String(10), primary_key=True)
    dimension = Column(String(20), primary_key=True)    # performance/valuation/growth/trend/business
    factor_name = Column(String(50), primary_key=True)  # 因子名 e.g. 'roe', 'pe_ttm'
    raw_value = Column(Float)
    z_score = Column(Float)                          # Z-score标准化值
    percentile = Column(Float)                       # 百分位排名(0-100)
    score = Column(Float)                            # 加权得分


class SectorChain(Base):
    """赛道因果链"""
    __tablename__ = "sector_chains"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_name = Column(String(200), nullable=False)  # 事件名称
    chain_json = Column(Text, nullable=False)         # 因果链JSON
    mapped_sectors = Column(Text)                     # 映射的板块(JSON数组)
    created_at = Column(String(20))


class TimingSignal(Base):
    """买点信号"""
    __tablename__ = "timing_signals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(6), nullable=False)
    signal_date = Column(String(10), nullable=False)    # 信号日期
    signal_type = Column(String(20), nullable=False)    # 'oversold' | 'breakout'
    signal_score = Column(Float)                        # 信号强度分(0-100)
    details_json = Column(Text)                         # 信号详情JSON
    created_at = Column(String(20))


class StockIntraday(Base):
    """分时数据（每分钟）"""
    __tablename__ = "stock_intraday"

    code = Column(String(6), primary_key=True)
    time = Column(String(19), primary_key=True)           # YYYY-MM-DD HH:MM:SS
    price = Column(Float)
    avg_price = Column(Float)                             # 均价
    volume = Column(Float)                                # 成交量(手)
    turnover = Column(Float)                              # 成交额(元)
    fetched_at = Column(String(20))


class StockDepth(Base):
    """盘口五档行情"""
    __tablename__ = "stock_depth"

    code = Column(String(6), primary_key=True)
    # 卖五→卖一
    ask5 = Column(Float); ask5_vol = Column(Float)
    ask4 = Column(Float); ask4_vol = Column(Float)
    ask3 = Column(Float); ask3_vol = Column(Float)
    ask2 = Column(Float); ask2_vol = Column(Float)
    ask1 = Column(Float); ask1_vol = Column(Float)
    # 买一→买五
    bid1 = Column(Float); bid1_vol = Column(Float)
    bid2 = Column(Float); bid2_vol = Column(Float)
    bid3 = Column(Float); bid3_vol = Column(Float)
    bid4 = Column(Float); bid4_vol = Column(Float)
    bid5 = Column(Float); bid5_vol = Column(Float)
    fetched_at = Column(String(20))
