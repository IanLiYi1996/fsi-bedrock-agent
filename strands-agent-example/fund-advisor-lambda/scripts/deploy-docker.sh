#!/bin/bash
# 基金顾问Lambda Docker部署脚本

set -e

# 切换到项目根目录
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

echo "=== 基金顾问Lambda Docker部署脚本 ==="
echo "项目根目录: $PROJECT_ROOT"

# 安装Node.js依赖
echo "=== 安装Node.js依赖 ==="
npm install

echo "${YELLOW}清理旧的构建目录...${NC}"
rm -rf dist

# 构建CDK应用
echo "=== 构建CDK应用 ==="
npm run build

# 部署CDK堆栈
echo "=== 部署CDK堆栈 ==="
cdk deploy

echo "=== 部署完成 ==="
