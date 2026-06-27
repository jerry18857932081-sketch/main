"""
A股量化选股分析平台 — FastAPI 入口
"""
import logging
import threading
import time as time_mod
from datetime import datetime, time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from backend.config import CORS_ORIGINS, HOST, PORT
from backend.database.connection import init_db, SessionLocal
from backend.services.data_pipeline import seed_data
from backend.services.live_pipeline import seed_real, fetch_spot_batch, fetch_kline, fetch_intraday

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# 全局状态
_scheduler_running = False
_last_spot_refresh = None
_demo_mode = False


def is_trading_time() -> bool:
    """判断当前是否在A股交易时段"""
    now = datetime.now()
    if now.weekday() >= 5:  # 周六日
        return False
    t = now.time()
    return time(9, 30) <= t <= time(15, 0)


def _scheduler_loop():
    """后台调度线程：演示模式全天更新，真实模式仅交易时段刷新"""
    global _last_spot_refresh, _demo_mode, _scheduler_running
    logger.info("后台调度器已启动")
    while _scheduler_running:
        try:
            can_refresh = _demo_mode or is_trading_time()
            if can_refresh:
                db = SessionLocal()
                try:
                    if _demo_mode:
                        # 演示模式：给行情加点随机噪音模拟实时变动
                        from backend.database.models import StockSpot
                        import numpy as np
                        spots = db.query(StockSpot).all()
                        rng = np.random.default_rng()
                        updated = 0
                        for s in spots[:200]:
                            if s.current_price and s.current_price > 0:
                                wiggle = rng.normal(0, 0.0015)
                                s.current_price = round(s.current_price * (1 + wiggle), 2)
                                s.change_pct = round((s.change_pct or 0) + wiggle * 100, 2)
                                s.volume = (s.volume or 0) + rng.uniform(100, 5000)
                                s.turnover = (s.turnover or 0) + rng.uniform(1e5, 5e6)
                                s.fetched_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                updated += 1
                        db.commit()
                        _last_spot_refresh = datetime.now().strftime("%H:%M:%S")
                        if updated > 0:
                            logger.debug(f"模拟行情更新: {updated} 只")
                    else:
                        n = fetch_spot_batch(db)
                        _last_spot_refresh = datetime.now().strftime("%H:%M:%S")
                        if n > 0:
                            logger.info(f"行情刷新: {n} 只")
                except Exception as e:
                    logger.error(f"调度刷新失败: {e}")
                    db.rollback()
                finally:
                    db.close()
            time_mod.sleep(30)
        except Exception as e:
            logger.error(f"调度器异常: {e}")
            time_mod.sleep(30)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    global _scheduler_running
    logger.info("初始化数据库...")
    init_db()
    logger.info("数据库就绪。如需种子数据请调用 POST /api/data/seed")
    _scheduler_running = True
    threading.Thread(target=_scheduler_loop, daemon=True).start()
    yield
    _scheduler_running = False


app = FastAPI(
    title="A股量化选股平台",
    description="五维立体选股 · 赛道推演 · 买点扫描",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.routers import market, stocks, screener, timing
app.include_router(market.router)
app.include_router(stocks.router)
app.include_router(screener.router)
app.include_router(timing.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "A股量化选股平台", "version": "1.0.0"}


@app.get("/api/status")
def system_status():
    """系统状态：数据新鲜度、调度器状态等"""
    return {
        "is_trading": is_trading_time(),
        "last_spot_refresh": _last_spot_refresh,
        "demo_mode": _demo_mode,
        "scheduler_alive": _scheduler_running,
    }


@app.post("/api/data/seed")
def trigger_seed(demo: bool = True, source: str = "demo"):
    """
    数据初始化。
    demo=true(source=demo): 模拟数据（离线可用）
    demo=false(source=eastmoney): 东方财富真实数据
    demo=false(source=akshare): akshare真实数据
    """
    global _demo_mode
    db = SessionLocal()
    try:
        if source == "eastmoney" or (not demo and source != "akshare"):
            _demo_mode = False
            seed_real(db)
            return {"status": "ok", "message": "真实数据初始化完成（东方财富）", "demo_mode": False}
        elif source == "akshare":
            _demo_mode = False
            seed_data(db, demo_mode=False)
            return {"status": "ok", "message": "真实数据初始化完成（akshare）", "demo_mode": False}
        else:
            _demo_mode = True
            seed_data(db, demo_mode=True)
            return {"status": "ok", "message": "演示数据初始化完成", "demo_mode": True}
    except Exception as e:
        logger.error(f"种子数据失败: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@app.post("/api/data/refresh")
def refresh_data(type: str = "spot"):
    """手动刷新数据"""
    global _last_spot_refresh
    db = SessionLocal()
    try:
        if type == "spot":
            if _demo_mode:
                # 演示模式手动触发价格波动
                from backend.database.models import StockSpot
                import numpy as np
                spots = db.query(StockSpot).all()
                rng = np.random.default_rng()
                for s in spots[:300]:
                    if s.current_price and s.current_price > 0:
                        s.current_price = round(s.current_price * (1 + rng.normal(0, 0.003)), 2)
                        s.change_pct = round((s.change_pct or 0) + rng.normal(0, 0.2), 2)
                        s.fetched_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                db.commit()
                n = 300
            else:
                from backend.services.data_pipeline import fetch_spot_data
                n = fetch_spot_data(db)
            _last_spot_refresh = datetime.now().strftime("%H:%M:%S")
        else:
            n = 0
        return {"status": "ok", "refreshed": n, "type": type, "timestamp": _last_spot_refresh}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


@app.post("/api/data/tick")
def force_tick():
    """手动触发一次价格模拟波动（演示模式用）"""
    global _last_spot_refresh
    if not _demo_mode:
        return {"status": "skipped", "reason": "非演示模式"}
    db = SessionLocal()
    try:
        from backend.database.models import StockSpot
        import numpy as np
        spots = db.query(StockSpot).all()
        rng = np.random.default_rng()
        updated = 0
        for s in spots[:200]:
            if s.current_price and s.current_price > 0:
                wiggle = rng.normal(0, 0.002)
                s.current_price = round(s.current_price * (1 + wiggle), 2)
                s.change_pct = round((s.change_pct or 0) + wiggle * 100, 2)
                s.fetched_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                updated += 1
        db.commit()
        _last_spot_refresh = datetime.now().strftime("%H:%M:%S")
        return {"status": "ok", "updated": updated, "timestamp": _last_spot_refresh}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=True)
