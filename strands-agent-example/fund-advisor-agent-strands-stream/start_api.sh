#!/bin/bash

# 检查是否安装了uvicorn
if ! command -v uvicorn &> /dev/null; then
    echo "uvicorn 未安装，正在安装..."
    pip install uvicorn
fi

# 启动FastAPI应用
echo "启动基金投顾API服务..."
echo "API文档将在 http://localhost:8000/docs 可用"
echo "Web界面将在 http://localhost:8000 可用"
echo "按 Ctrl+C 停止服务"

# 使用uvicorn启动应用，启用热重载
uvicorn app:app --reload --host 0.0.0.0 --port 8000
