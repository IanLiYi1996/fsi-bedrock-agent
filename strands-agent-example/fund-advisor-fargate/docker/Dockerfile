FROM --platform=linux/amd64 public.ecr.aws/docker/library/python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements.txt并安装Python依赖
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app/ .

COPY app/agents/ ./app/agents/
COPY app/knowledge/ ./app/knowledge/
COPY app/tools/ ./app/tools/
COPY app/auth/ ./app/auth/

# 创建非root用户运行应用
RUN useradd -m appuser
USER appuser

# 暴露应用端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]