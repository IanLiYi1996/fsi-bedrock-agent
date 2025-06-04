# 基金投顾多Agent系统 - AWS Lambda部署

本项目将基于Strands Agents的基金投顾多Agent系统部署到AWS Lambda上，实现无服务器、可扩展、低成本的投资顾问服务。通过Lambda部署，使基金投顾系统能够按需扩展，并且只在处理请求时产生费用。

## 项目概述

基金投顾多Agent系统是一个基于Strands Agents框架实现的智能投资顾问系统，由多个专业Agent协作完成用户查询处理。本项目将原有的Fargate容器部署改造为Lambda无服务器部署。

### 核心功能

- 基金分析与推荐
- 投资组合评估与优化
- 市场趋势分析
- 用户风险偏好评估
- 基金经理能力分析

## 架构设计

![架构图](https://via.placeholder.com/800x400?text=Fund+Advisor+Lambda+Architecture)

### 系统组件

- **Lambda函数**：处理用户查询的无服务器函数
- **Lambda层**：包含依赖的可重用层
- **多Agent系统**：包含多个专业Agent的协作系统
- **知识库**：基金投资相关知识
- **数据工具**：访问和处理基金数据的工具

### AWS服务集成

- **AWS Lambda**：无服务器函数运行环境
- **Amazon DynamoDB**：存储用户数据和会话状态
- **Amazon Bedrock**：提供大语言模型能力
- **AWS IAM**：身份和访问管理
- **Amazon CloudWatch**：监控和日志

## 目录结构

```
fund-advisor-lambda/
├── bin/                    # CDK应用入口和部署脚本
│   ├── cdk-app.ts          # CDK应用定义
│   └── package_for_lambda.py  # Lambda打包脚本
├── lib/                    # CDK堆栈定义
│   └── fund-advisor-lambda-stack.ts  # Lambda堆栈
├── lambda/                 # Lambda函数代码
│   ├── agent_handler.py    # Lambda处理程序
│   ├── agents/             # Agent代码
│   └── utils/              # 工具函数
├── packaging/              # Lambda部署包
│   ├── app.zip             # 应用代码包
│   └── dependencies.zip    # 依赖包
├── cdk.json                # CDK配置
├── package.json            # 依赖定义
├── tsconfig.json           # TypeScript配置
└── requirements.txt        # Python依赖
```

## 技术栈

- **Agent框架**：Strands Agents
- **大语言模型**：Amazon Bedrock (Claude)
- **无服务器**：AWS Lambda
- **基础设施即代码**：AWS CDK (TypeScript)
- **数据存储**：Amazon DynamoDB

## 部署步骤

### 前提条件

- AWS账户和配置好的AWS CLI凭证
- Node.js 18+
- Python 3.12+
- AWS CDK

### 1. 准备环境

克隆项目并安装依赖：

```bash
git clone <repository-url>
cd fund-advisor-lambda

# 安装Node.js依赖
npm install

# 安装Python依赖
pip install -r requirements.txt

# 安装Lambda依赖
pip install -r requirements.txt --platform manylinux2014_aarch64 --target ./packaging/_dependencies --only-binary=:all:
```

### 2. 打包Lambda函数

```bash
python ./bin/package_for_lambda.py
```

### 3. 部署CDK堆栈

```bash
npm run build
cdk deploy
```

### 4. 测试Lambda函数

```bash
# 使用AWS CLI调用Lambda函数
aws lambda invoke --function-name FundAdvisorFunction \
      --region us-east-1 \
      --cli-binary-format raw-in-base64-out \
      --payload '{"query": "推荐一些低风险基金"}' \
      output.json

# 查看结果
cat output.json
```

## 性能优化

本项目在Lambda部署中进行了以下性能优化：

1. **Lambda层**：使用Lambda层存储依赖，减少冷启动时间
2. **内存配置**：根据Agent复杂度调整Lambda内存
3. **超时设置**：设置适当的超时时间，确保复杂查询能够完成
4. **代码优化**：简化回调处理器和上下文工具函数，减少不必要的复杂性

## 安全考虑

1. **IAM权限最小化**：仅授予必要的权限
2. **敏感信息管理**：使用环境变量存储配置
3. **日志监控**：配置CloudWatch日志和告警

## 监控和日志

- **CloudWatch指标**：监控Lambda调用次数、持续时间和错误
- **应用日志**：结构化日志输出到CloudWatch Logs
- **告警设置**：关键指标超阈值时触发告警

## 与Fargate版本的区别

1. **部署模型**：从容器化部署转为无服务器部署
2. **API处理**：从FastAPI应用转为Lambda处理程序
3. **资源配置**：从容器资源配置转为Lambda资源配置
4. **状态管理**：从长时间运行的服务转为无状态函数
5. **成本模型**：从按容器运行时间计费转为按调用次数和执行时间计费

## 清理

要删除所有创建的资源：

```bash
cdk destroy
```

## 故障排除

### 常见问题

1. **部署失败**
   - 检查AWS凭证是否有效
   - 确认IAM权限是否足够
   - 查看CloudFormation事件日志

2. **Lambda执行超时**
   - 增加Lambda超时设置
   - 优化代码执行效率
   - 考虑增加Lambda内存

3. **依赖问题**
   - 确保依赖安装到正确的目录
   - 检查依赖版本兼容性
   - 验证Lambda层是否正确创建

## 贡献指南

欢迎贡献代码、报告问题或提出改进建议。请遵循以下步骤：

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

[MIT](LICENSE)

## 联系方式

如有问题或建议，请联系项目维护者。
