#!/bin/bash
set -e

# 打印环境信息
echo "Starting English Mastery API..."
echo "PORT: ${PORT:-8000}"
echo "Working directory: $(pwd)"
echo "Python version: $(python --version)"

# 使用 PORT 环境变量，默认 8000
PORT=${PORT:-8000}

# 启动 uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
