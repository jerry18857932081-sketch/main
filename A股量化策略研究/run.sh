#!/bin/bash
# 启动 A股量化选股平台 后端服务
cd "$(dirname "$0")"
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
