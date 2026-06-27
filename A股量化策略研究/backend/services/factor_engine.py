"""
五维因子引擎
对全市场A股计算五维立体因子分：
  1. 当下业绩 (Performance)
  2. 估值匹配 (Valuation)
  3. 未来成长 (Growth)
  4. 产业趋势 (Trend)
  5. 商业模式 (Business)

每个因子：原始值 → Z-score标准化 → 方向校正 → 加权得分
"""
import logging
from datetime import datetime
from collections import defaultdict

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from backend.database.models import StockUniverse, StockSpot, StockFinancial, StockFactor

logger = logging.getLogger(__name__)

# ========== 因子定义 ==========
# 每个因子: (维度, 因子名, 显示名, 方向, 默认权重)
# 方向: 'higher_better' | 'lower_better'
FACTOR_DEFINITIONS = {
    # ---- 当下业绩 ----
    "roe":           ("performance", "roe",            "ROE",              "higher_better", 8),
    "gross_margin":  ("performance", "gross_margin",   "毛利率",            "higher_better", 6),
    "net_margin":    ("performance", "net_margin",     "净利率",            "higher_better", 6),
    "profit_yoy":    ("performance", "profit_yoy",     "利润同比增速",       "higher_better", 5),

    # ---- 估值匹配 ----
    "pe_ttm":        ("valuation",   "pe_ttm",         "市盈率(TTM)",       "lower_better",  8),
    "pb":            ("valuation",   "pb",             "市净率",            "lower_better",  6),
    "peg":           ("valuation",   "peg",            "PEG",              "lower_better",  6),

    # ---- 未来成长 ----
    "revenue_yoy":   ("growth",      "revenue_yoy",    "营收同比增速",       "higher_better", 8),
    "eps":           ("growth",      "eps",            "每股收益",          "higher_better", 6),
    "bvps":          ("growth",      "bvps",           "每股净资产",         "higher_better", 5),
    "debt_ratio":    ("growth",      "debt_ratio",     "资产负债率(反向)",   "lower_better",  6),

    # ---- 产业趋势 ----
    # 产业趋势难以直接从财报量化，此处用代理指标：
    # - 毛利率趋势（近两期变化）作为行业景气代理
    # - 营收增速持续性
    "margin_trend":  ("trend",       "margin_trend",   "毛利率趋势",         "higher_better", 8),
    "rev_growth_stability": ("trend","rev_growth_stability", "营收增长持续性","higher_better", 7),

    # ---- 商业模式 ----
    "gross_margin_level": ("business", "gross_margin_level", "毛利率水平",   "higher_better", 8),
    "current_ratio": ("business",     "current_ratio",  "流动比率",          "higher_better", 4),
    "op_cash_flow_ratio": ("business", "op_cash_flow_ratio", "经营现金流/利润","higher_better", 3),
}

# 维度元数据（前端展示）
DIMENSION_NAMES = {
    "performance": "当下业绩",
    "valuation":   "估值匹配",
    "growth":      "未来成长",
    "trend":       "产业趋势",
    "business":    "商业模式",
}


def _safe_float(val, default=np.nan):
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def build_factor_dataframe(session: Session):
    """
    从数据库构建因子计算用的宽表DataFrame。
    每一行是一只股票，列为各因子的原始值。
    """
    spots = session.query(StockSpot).all()
    if not spots:
        return pd.DataFrame()

    rows = []
    for s in spots:
        # 取最新一期财务数据
        fin = session.query(StockFinancial).filter_by(code=s.code).order_by(
            StockFinancial.report_period.desc()
        ).first()

        # 取上一期财务数据（用于趋势计算）
        fin_prev = session.query(StockFinancial).filter_by(code=s.code).order_by(
            StockFinancial.report_period.desc()
        ).offset(1).first()

        # 基础信息
        universe = session.query(StockUniverse).filter_by(code=s.code).first()
        if not universe or universe.is_st:
            continue  # 跳过ST

        row = {
            "code": s.code,
            "name": s.name or universe.name if universe else "",
            "industry_l1": universe.industry_l1 if universe else "",
            "industry_l2": universe.industry_l2 if universe else "",
            "market_cap": universe.market_cap if universe else None,
        }

        # 行情指标
        row["pe_ttm"] = _safe_float(s.pe_ttm)
        row["pb"] = _safe_float(s.pb)
        row["current_price"] = _safe_float(s.current_price)
        row["change_pct"] = _safe_float(s.change_pct)

        # 财务指标
        if fin:
            row["roe"] = _safe_float(fin.roe)
            row["gross_margin"] = _safe_float(fin.gross_margin)
            row["net_margin"] = _safe_float(fin.net_margin)
            row["revenue_yoy"] = _safe_float(fin.revenue_yoy)
            row["profit_yoy"] = _safe_float(fin.profit_yoy)
            row["eps"] = _safe_float(fin.eps)
            row["bvps"] = _safe_float(fin.bvps)
            row["debt_ratio"] = _safe_float(fin.debt_ratio)
            row["current_ratio"] = _safe_float(fin.current_ratio)
            row["op_cash_flow"] = _safe_float(fin.op_cash_flow)

            # PEG = PE / (利润增速 * 100)（简化版）
            profit_growth = _safe_float(fin.profit_yoy)
            pe = _safe_float(s.pe_ttm)
            if profit_growth and profit_growth > 0 and pe and pe > 0:
                row["peg"] = pe / (profit_growth * 100)
            else:
                row["peg"] = np.nan

            # 经营现金流/利润比（用当前eps近似）
            op_cf = _safe_float(fin.op_cash_flow)
            if op_cf and op_cf > 0:
                row["op_cash_flow_ratio"] = op_cf / max(abs(profit_growth or 1), 1)
            else:
                row["op_cash_flow_ratio"] = np.nan

            # 毛利率趋势（环比变化）
            if fin_prev:
                prev_margin = _safe_float(fin_prev.gross_margin)
                curr_margin = _safe_float(fin.gross_margin)
                if not np.isnan(prev_margin) and not np.isnan(curr_margin):
                    row["margin_trend"] = curr_margin - prev_margin
                else:
                    row["margin_trend"] = 0.0

                # 营收增长持续性（本季度增速 vs 上季度增速）
                prev_rev = _safe_float(fin_prev.revenue_yoy)
                curr_rev = _safe_float(fin.revenue_yoy)
                if not np.isnan(prev_rev) and not np.isnan(curr_rev):
                    row["rev_growth_stability"] = curr_rev - prev_rev
                else:
                    row["rev_growth_stability"] = 0.0
            else:
                row["margin_trend"] = 0.0
                row["rev_growth_stability"] = 0.0

        # 商业模式维度
        # 毛利率水平复用了基本面的gross_margin，这里单独保存
        row["gross_margin_level"] = row.get("gross_margin", np.nan)

        rows.append(row)

    df = pd.DataFrame(rows)
    return df


def winsorize(series: pd.Series, limits: float = 3.0) -> pd.Series:
    """Winsorize 缩尾处理：将极端值拉到 limits 个标准差内"""
    mean = series.mean()
    std = series.std()
    if std == 0 or np.isnan(std):
        return series
    lower = mean - limits * std
    upper = mean + limits * std
    return series.clip(lower, upper)


def compute_factors(session: Session):
    """
    主入口：计算全市场五维因子分并写入 stock_factors 表。
    返回因子DataFrame。
    """
    df = build_factor_dataframe(session)
    if df.empty:
        logger.warning("因子计算：无数据")
        return df

    calc_date = datetime.now().strftime("%Y-%m-%d")

    # 清除今日旧数据
    session.query(StockFactor).filter_by(calc_date=calc_date).delete()
    session.commit()

    # 逐因子进行 Z-score 标准化 + 方向校正 + 打分
    all_scores = {}  # code -> {dimension: data}

    for factor_name, (dimension, _fname, _display, direction, weight) in FACTOR_DEFINITIONS.items():
        if factor_name not in df.columns:
            continue

        series = df[factor_name].copy()
        # 移除极端值
        series = winsorize(series)
        # 排除 NaN
        valid_mask = series.notna()
        if valid_mask.sum() < 5:
            continue

        mean = series[valid_mask].mean()
        std = series[valid_mask].std()
        if std == 0:
            continue

        z_scores = pd.Series(np.nan, index=df.index)
        z_scores[valid_mask] = (series[valid_mask] - mean) / std

        # 方向校正：lower_better 的因子取反
        if direction == "lower_better":
            z_scores = -z_scores

        # 百分位 (percentile)
        # 用正态CDF近似
        from scipy.stats import norm
        percentiles = pd.Series(np.nan, index=df.index)
        percentiles[valid_mask] = norm.cdf(z_scores[valid_mask]) * 100

        # 加权分 = z_score * weight
        scores = z_scores * weight

        # 写入数据库
        for idx in df.index:
            code = df.loc[idx, "code"]
            raw_val = df.loc[idx, factor_name]
            z = z_scores[idx]
            p = percentiles[idx]
            s = scores[idx]

            if code not in all_scores:
                all_scores[code] = {
                    "dimensions": defaultdict(lambda: 0.0),
                    "factors": {},
                    "raw": {},
                    "z": {},
                    "p": {},
                }

            all_scores[code]["dimensions"][dimension] += s if not np.isnan(s) else 0
            all_scores[code]["factors"][factor_name] = s if not np.isnan(s) else 0
            all_scores[code]["z"][factor_name] = z if not np.isnan(z) else 0
            all_scores[code]["p"][factor_name] = p if not np.isnan(p) else 50

            if not np.isnan(raw_val):
                session.add(StockFactor(
                    code=code,
                    calc_date=calc_date,
                    dimension=dimension,
                    factor_name=factor_name,
                    raw_value=raw_val,
                    z_score=round(z, 4) if not np.isnan(z) else None,
                    percentile=round(p, 2) if not np.isnan(p) else None,
                    score=round(s, 4) if not np.isnan(s) else None,
                ))

    session.commit()
    logger.info(f"因子计算完成: {len(all_scores)} 只股票, {calc_date}")

    # 将得分信息附加到DataFrame
    df["dimension_scores"] = df["code"].apply(
        lambda c: dict(all_scores.get(c, {}).get("dimensions", {}))
    )
    df["factor_scores"] = df["code"].apply(
        lambda c: dict(all_scores.get(c, {}).get("factors", {}))
    )
    df["calc_date"] = calc_date

    return df


def get_factor_meta():
    """返回全部因子元数据（供前端展示）"""
    meta = []
    for factor_name, (dimension, _fname, display, direction, weight) in FACTOR_DEFINITIONS.items():
        meta.append({
            "dimension": dimension,
            "dimension_name": DIMENSION_NAMES.get(dimension, dimension),
            "factor_name": factor_name,
            "display_name": display,
            "description": f"{display} — {'越高越好' if direction == 'higher_better' else '越低越好'}",
            "direction": direction,
            "default_weight": weight,
        })
    return meta
