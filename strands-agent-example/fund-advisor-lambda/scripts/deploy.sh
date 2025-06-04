#!/bin/bash
# 基金顾问Lambda部署脚本
# 此脚本用于安装依赖、打包Lambda函数并部署CDK堆栈

set -e

# 切换到项目根目录
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

echo "=== 基金顾问Lambda部署脚本 ==="
echo "项目根目录: $PROJECT_ROOT"

# 安装Node.js依赖
echo "=== 安装Node.js依赖 ==="
npm install

rm -rf ./venv
# 安装Python
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install --upgrade pip

# 安装Python依赖（用于本地开发）
echo "=== 安装Python依赖（用于本地开发） ==="
pip install -r requirements.txt

# 安装Lambda依赖（用于Lambda部署）
echo "=== 安装Lambda依赖（用于Lambda部署） ==="
rm -rf packaging/_dependencies/*
pip install -r requirements.txt --platform manylinux2014_x86_64 --target ./packaging/_dependencies --only-binary=:all:
pip install -r requirements-extra.txt --platform manylinux2014_x86_64 --target ./packaging/_dependencies --only-binary=:all:
pip install "jsonpath>=0.82" --no-deps --platform manylinux2014_x86_64 --target ./packaging/_dependencies
pip install akshare --no-deps --platform manylinux2014_x86_64 --target ./packaging/_dependencies


echo "${YELLOW}清理旧的构建目录...${NC}"
rm -rf dist

# 打包Lambda函数
echo "=== 打包Lambda函数 ==="
python ./bin/package_for_lambda.py

# 构建CDK应用
echo "=== 构建CDK应用 ==="
npm run build

# 部署CDK堆栈
echo "=== 部署CDK堆栈 ==="
cdk deploy

echo "=== 部署完成 ==="