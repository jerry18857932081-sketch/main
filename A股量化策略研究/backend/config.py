"""应用配置"""
import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数据库
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'platform.db')}"

# 服务
HOST = "0.0.0.0"
PORT = 8000

# CORS (Vite dev server)
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# 缓存策略（秒）
SPOT_CACHE_TTL = 300        # 行情快照 5分钟
FINANCIAL_CACHE_TTL = 86400 # 财务数据 1天
DAILY_KLINE_CACHE_TTL = 3600 # 日K线 1小时

# akshare 请求间隔（秒），避免被限流
AKSHARE_RATE_LIMIT = 0.5

# 五维因子默认权重
DEFAULT_DIMENSION_WEIGHTS = {
    "performance": 25,   # 当下业绩
    "valuation": 20,     # 估值匹配
    "growth": 25,        # 未来成长
    "trend": 15,         # 产业趋势
    "business": 15,      # 商业模式
}
