#!/bin/bash
set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}===== 基金投顾多Agent系统 Fargate部署脚本 =====${NC}"

# 检查AWS CLI是否已安装
if ! command -v aws &> /dev/null; then
    echo -e "${RED}错误: AWS CLI未安装. 请先安装AWS CLI.${NC}"
    exit 1
fi

# 检查AWS凭证
echo -e "${YELLOW}检查AWS凭证...${NC}"
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}错误: AWS凭证无效或未配置. 请运行 'aws configure' 配置凭证.${NC}"
    exit 1
fi
echo -e "${GREEN}AWS凭证有效.${NC}"

# 检查CDK是否已安装
if ! command -v cdk &> /dev/null; then
    echo -e "${YELLOW}CDK未安装, 正在安装...${NC}"
    npm install -g aws-cdk
fi

# 准备知识库和DynamoDB
# echo -e "${YELLOW}准备知识库和DynamoDB...${NC}"
# if [ -f "../fund-advisor-agent-strands/deploy_prereqs.sh" ]; then
#     echo -e "${YELLOW}运行原始项目的先决条件脚本...${NC}"
#     cd ../fund-advisor-agent-strands
#     sh deploy_prereqs.sh
#     cd ../fund-advisor-fargate/scripts
# else
#     echo -e "${RED}警告: 找不到原始项目的先决条件脚本. 请确保知识库和DynamoDB已经创建.${NC}"
# fi

# 部署CDK堆栈
echo -e "${YELLOW}部署CDK堆栈...${NC}"
cd ../cdk

# 删除旧的构建目录
if [ -d "dist" ]; then
    echo -e "${YELLOW}清理旧的构建目录...${NC}"
    rm -rf dist
    echo -e "${GREEN}旧的构建目录已清理.${NC}"
fi

# 安装依赖
echo -e "${YELLOW}安装CDK依赖...${NC}"
npm install

# 构建TypeScript代码
echo -e "${YELLOW}构建TypeScript代码...${NC}"
npm run build

# 部署堆栈
echo -e "${YELLOW}部署CDK堆栈...${NC}"
cdk deploy --require-approval never

# 获取API端点
echo -e "${YELLOW}获取API端点...${NC}"
API_ENDPOINT=$(aws cloudformation describe-stacks --stack-name FundAdvisorFargateStack --query "Stacks[0].Outputs[?OutputKey=='FundAdvisorServiceEndpoint'].OutputValue" --output text)

echo -e "${GREEN}部署完成!${NC}"
echo -e "${GREEN}API端点: ${YELLOW}http://$API_ENDPOINT${NC}"
echo -e "${GREEN}测试API: ${YELLOW}curl -X POST http://$API_ENDPOINT/advisor -H \"Content-Type: application/json\" -d '{\"query\":\"推荐一些低风险基金\"}'${NC}"