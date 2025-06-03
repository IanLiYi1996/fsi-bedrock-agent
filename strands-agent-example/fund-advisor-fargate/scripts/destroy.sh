#!/bin/bash
set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "${GREEN}===== 基金投顾多Agent系统 Fargate销毁脚本 =====${NC}"

# 检查AWS CLI是否已安装
if ! command -v aws &> /dev/null; then
    echo "${RED}错误: AWS CLI未安装. 请先安装AWS CLI.${NC}"
    exit 1
fi

# 检查AWS凭证
echo "${YELLOW}检查AWS凭证...${NC}"
if ! aws sts get-caller-identity &> /dev/null; then
    echo "${RED}错误: AWS凭证无效或未配置. 请运行 'aws configure' 配置凭证.${NC}"
    exit 1
fi
echo "${GREEN}AWS凭证有效.${NC}"

# 检查CDK是否已安装
if ! command -v cdk &> /dev/null; then
    echo "${RED}错误: CDK未安装. 请先安装CDK.${NC}"
    exit 1
fi

# 确认销毁操作
echo "${RED}警告: 此操作将销毁所有与基金投顾多Agent系统相关的AWS资源.${NC}"
read -p "确定要继续吗? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "${YELLOW}操作已取消.${NC}"
    exit 0
fi

# 销毁CDK堆栈
echo "${YELLOW}销毁CDK堆栈...${NC}"
cd ../cdk

# 安装依赖（如果需要）
echo "${YELLOW}安装CDK依赖...${NC}"
npm install

# 销毁堆栈
echo "${YELLOW}销毁FundAdvisorFargateStack堆栈...${NC}"
cdk destroy FundAdvisorFargateStack --force

# 清理本地资源（如果有）
echo "${YELLOW}清理本地资源...${NC}"
if [ -d "dist" ]; then
    echo "${YELLOW}删除构建目录...${NC}"
    rm -rf dist
    echo "${GREEN}构建目录已删除.${NC}"
fi

# 清理日志文件（如果有）
if [ -f "../docker/app/logs/fund_advisor_api.log" ]; then
    echo "${YELLOW}删除日志文件...${NC}"
    rm -f ../docker/app/logs/fund_advisor_api.log
    echo "${GREEN}日志文件已删除.${NC}"
fi

echo "${GREEN}销毁完成!${NC}"
echo "${GREEN}所有与基金投顾多Agent系统相关的AWS资源已被删除.${NC}"
