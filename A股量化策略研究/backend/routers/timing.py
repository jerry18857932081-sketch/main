"""买点扫描路由（Phase 2 实现）"""
import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.database.connection import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/timing", tags=["timing"])


@router.get("/oversold")
def get_oversold_signals(
    min_score: float = Query(50, description="最低信号分"),
    sector: str = Query(None, description="申万一级行业"),
    db: Session = Depends(get_db),
):
    """
    超跌反弹信号扫描。
    Phase 2 实现完整逻辑，当前返回空列表。
    """
    return {"signals": [], "scan_date": "", "total": 0}


@router.get("/breakout")
def get_breakout_signals(
    min_score: float = Query(50, description="最低信号分"),
    sector: str = Query(None, description="申万一级行业"),
    db: Session = Depends(get_db),
):
    """
    压力突破信号扫描。
    Phase 2 实现完整逻辑，当前返回空列表。
    """
    return {"signals": [], "scan_date": "", "total": 0}


@router.get("/signals/{code}")
def get_stock_signals(code: str, db: Session = Depends(get_db)):
    """获取某只股票的历史买点信号"""
    return {"code": code, "signals": []}
