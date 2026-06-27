# A股量化策略研究

A-share quantitative strategy research project.

## 目录结构

```
├── data/                  # 数据存储
│   ├── raw/              # 原始数据（行情、财务、资金流等）
│   ├── processed/        # 清洗后的数据
│   └── cache/            # 本地缓存
├── strategies/           # 策略实现
│   ├── momentum/         # 动量策略
│   ├── mean_reversion/   # 均值回归策略
│   ├── multi_factor/     # 多因子策略
│   └── arbitrage/        # 套利策略
├── backtest/             # 回测引擎与回测脚本
├── research/             # Jupyter Notebooks 研究笔记
├── utils/                # 工具函数（数据获取、指标计算等）
├── config/               # 配置文件（数据源、参数等）
└── README.md
```

## 数据源

- Tushare / AkShare / Baostock
- 东方财富 / 新浪财经 API
- 本地数据文件

## 快速开始

```bash
pip install akshare pandas numpy matplotlib backtrader
```
