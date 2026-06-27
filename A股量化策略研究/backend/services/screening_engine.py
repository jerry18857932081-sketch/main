"""
五维筛选引擎
根据用户指定的筛选条件和维度权重，对全市场股票打分排名。
"""
import logging
from typing import Optional
from collections import defaultdict

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from backend.services.factor_engine import compute_factors, FACTOR_DEFINITIONS
from backend.database.models import StockUniverse, StockSpot

logger = logging.getLogger(__name__)


def run_screening(
    session: Session,
    filters: list[dict],
    dimension_weights: dict[str, float],
    sector: Optional[str] = None,
    universe: str = "all",
    limit: int = 50,
    sort_by: str = "total_score",
    order: str = "desc",
) -> dict:
    """
    执行五维筛选。

    参数:
        session: 数据库会话
        filters: [{"factor": "pe_ttm", "min": None, "max": 50}, ...]
        dimension_weights: {"performance": 25, "valuation": 20, ...}
        sector: 申万一级行业名（筛选范围），None=全市场
        universe: 'all' | 'main' | 'gem' | 'star'
        limit: 返回条数
        sort_by: 排序字段
        order: 'asc' | 'desc'

    返回:
        {"total_matched": int, "results": [...], "meta": {...}}
    """
    # 1. 计算/获取因子
    df = compute_factors(session)
    if df.empty:
        return {"total_matched": 0, "results": [], "meta": {"error": "无可用数据"}}

    # 2. 应用 universe 过滤
    df = _filter_universe(df, universe, session)

    # 3. 应用 sector 过滤
    if sector:
        df = df[df["industry_l1"] == sector].copy()

    universe_size = len(df)
    if universe_size == 0:
        return {"total_matched": 0, "results": [], "meta": {"universe_size": 0}}

    # 4. 应用阈值过滤
    for f in filters:
        factor = f.get("factor", "")
        vmin = f.get("min")
        vmax = f.get("max")
        if factor not in df.columns:
            continue
        if vmin is not None:
            df = df[df[factor] >= vmin].copy()
        if vmax is not None:
            df = df[df[factor] <= vmax].copy()

    if df.empty:
        return {
            "total_matched": 0,
            "results": [],
            "meta": {"universe_size": universe_size, "filters_applied": len(filters)},
        }

    # 5. 计算综合得分
    df["total_score"] = 0.0
    for dim, weight in dimension_weights.items():
        if weight == 0:
            continue
        # 从 factor_scores 列中聚合维度分
        score_col = f"dim_{dim}_score"
        df[score_col] = df["dimension_scores"].apply(
            lambda d: d.get(dim, 0) if isinstance(d, dict) else 0
        )
        # 归一化维度分到 0-100
        dim_min = df[score_col].min()
        dim_max = df[score_col].max()
        if dim_max > dim_min:
            df[score_col + "_norm"] = (df[score_col] - dim_min) / (dim_max - dim_min) * 100
        else:
            df[score_col + "_norm"] = 50.0
        df["total_score"] += df[score_col + "_norm"] * weight / 100

    # 6. 排序
    ascending = order == "asc"
    df = df.sort_values(sort_by if sort_by in df.columns else "total_score",
                        ascending=ascending)

    # 7. 取 Top N
    df_top = df.head(limit).copy()
    df_top["rank"] = range(1, len(df_top) + 1)

    # 8. 组装结果
    results = []
    for _, row in df_top.iterrows():
        dim_scores = {}
        for dim in dimension_weights:
            col = f"dim_{dim}_score_norm"
            dim_scores[dim] = round(float(row.get(col, 0)), 1)

        factor_scores = row.get("factor_scores", {})
        if isinstance(factor_scores, dict):
            factor_scores_out = {k: round(float(v), 2) for k, v in factor_scores.items()}
        else:
            factor_scores_out = {}

        results.append({
            "rank": int(row["rank"]),
            "code": str(row["code"]),
            "name": str(row.get("name", "")),
            "industry_l1": str(row.get("industry_l1", "")),
            "current_price": float(row.get("current_price", 0)) if not pd.isna(row.get("current_price", np.nan)) else None,
            "change_pct": float(row.get("change_pct", 0)) if not pd.isna(row.get("change_pct", np.nan)) else None,
            "pe_ttm": float(row.get("pe_ttm", 0)) if not pd.isna(row.get("pe_ttm", np.nan)) else None,
            "pb": float(row.get("pb", 0)) if not pd.isna(row.get("pb", np.nan)) else None,
            "roe": float(row.get("roe", 0)) if not pd.isna(row.get("roe", np.nan)) else None,
            "total_score": round(float(row["total_score"]), 2),
            "dimension_scores": dim_scores,
            "factor_scores": factor_scores_out,
        })

    return {
        "total_matched": len(df),
        "results": results,
        "meta": {
            "universe_size": universe_size,
            "filters_applied": len(filters),
            "factor_count": len(FACTOR_DEFINITIONS),
            "calc_date": str(df.iloc[0].get("calc_date", "")) if len(df) > 0 else "",
        },
    }


def _filter_universe(df: pd.DataFrame, universe: str, session: Session) -> pd.DataFrame:
    """根据板块过滤"""
    if universe == "all":
        return df.copy()
    if universe == "main":
        # 主板：60xxxx(沪) + 00xxxx(深)
        return df[df["code"].str.match(r"^(60|00)")].copy()
    if universe == "gem":
        # 创业板：30xxxx
        return df[df["code"].str.match(r"^30")].copy()
    if universe == "star":
        # 科创板：68xxxx
        return df[df["code"].str.match(r"^68")].copy()
    return df.copy()
