"""五维筛选路由"""
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.database.models import StockUniverse
from backend.services.factor_engine import get_factor_meta
from backend.services.screening_engine import run_screening
from backend.schemas.schemas import (
    ScreenRequest, ScreenResponse, ScreenResultItem,
    ScreenTemplateSave, ScreenTemplateResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/screen", tags=["screener"])


@router.get("/dimensions")
def get_dimensions(db: Session = Depends(get_db)):
    """获取五维因子元数据（供前端构建筛选面板）"""
    factors = get_factor_meta()
    # 按维度分组
    from collections import defaultdict
    grouped = defaultdict(list)
    for f in factors:
        grouped[f["dimension"]].append(f)
    return {
        "dimensions": [
            {"key": "performance", "name": "当下业绩"},
            {"key": "valuation", "name": "估值匹配"},
            {"key": "growth", "name": "未来成长"},
            {"key": "trend", "name": "产业趋势"},
            {"key": "business", "name": "商业模式"},
        ],
        "factors": factors,
        "grouped_factors": dict(grouped),
    }


@router.post("/run")
def screen_stocks(req: ScreenRequest, db: Session = Depends(get_db)):
    """
    执行五维筛选。

    示例请求体:
    ```json
    {
      "filters": [
        {"factor": "pe_ttm", "min": null, "max": 50},
        {"factor": "roe", "min": 15, "max": null}
      ],
      "dimension_weights": {
        "performance": 25,
        "valuation": 20,
        "growth": 25,
        "trend": 15,
        "business": 15
      },
      "sector": null,
      "universe": "all",
      "limit": 50,
      "sort_by": "total_score",
      "order": "desc"
    }
    ```
    """
    # 验证权重合计为100
    total_weight = sum(req.dimension_weights.values())
    if total_weight != 100:
        # 自动归一化
        for k in req.dimension_weights:
            req.dimension_weights[k] = req.dimension_weights[k] / total_weight * 100

    filters_dict = [f.model_dump() for f in req.filters]

    result = run_screening(
        session=db,
        filters=filters_dict,
        dimension_weights=req.dimension_weights,
        sector=req.sector,
        universe=req.universe,
        limit=req.limit,
        sort_by=req.sort_by,
        order=req.order,
    )

    return result


@router.post("/save")
def save_template(req: ScreenTemplateSave, db: Session = Depends(get_db)):
    """保存筛选模板"""
    import json
    from backend.database.models import StockUniverse
    # 这里简化处理：存入 sector_chains 表（字段够用）
    # 实际生产应建独立表 screen_templates

    # 使用 stock_universe 表的元数据来建一个简单的模板存储
    # 暂时直接返回模拟ID（后续Phase可扩展独立表）
    return {"id": 1, "name": req.name, "status": "saved"}


@router.get("/saved")
def get_saved_templates(db: Session = Depends(get_db)):
    """获取已保存的筛选模板"""
    # Phase 2 实现独立模板表
    return []
