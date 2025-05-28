# 基金投顾多Agent系统 - AWS Fargate部署

本项目将基于Strands Agents的基金投顾多Agent系统部署到AWS Fargate上，实现高可用、可扩展、低运维成本的Web服务。通过容器化部署和云原生架构，使基金投顾系统能够更好地应对变化的负载需求。

## 项目概述

基金投顾多Agent系统是一个基于Strands Agents框架实现的智能投资顾问系统，由多个专业Agent协作完成用户查询处理。本项目将原有的命令行交互式应用改造为RESTful API服务，并使用AWS Fargate进行容器化部署。

### 核心功能

- 基金分析与推荐
- 投资组合评估与优化
- 市场趋势分析
- 用户风险偏好评估
- 基金经理能力分析

## 架构设计

![架构图](https://via.placeholder.com/800x400?text=Fund+Advisor+Fargate+Architecture)

### 系统组件

- **Web API层**：FastAPI应用，提供RESTful接口
- **多Agent系统**：包含多个专业Agent的协作系统
- **知识库**：基金投资相关知识
- **数据工具**：访问和处理基金数据的工具
- **AWS基础设施**：Fargate、ALB、DynamoDB等

### AWS服务集成

- **AWS Fargate**：无服务器容器运行环境
- **Amazon ECS**：容器编排服务
- **Application Load Balancer**：负载均衡和健康检查
- **Amazon DynamoDB**：存储用户数据和会话状态
- **Amazon Bedrock**：提供大语言模型能力
- **AWS IAM**：身份和访问管理
- **Amazon CloudWatch**：监控和日志

## 目录结构

```
fund-advisor-fargate/
├── cdk/                    # CDK基础设施代码
│   ├── bin/                # CDK应用入口
│   │   └── cdk-app.ts      # CDK应用定义
│   ├── lib/                # CDK堆栈定义
│   │   └── fund-advisor-fargate-stack.ts  # Fargate堆栈
│   ├── cdk.json            # CDK配置
│   ├── package.json        # 依赖定义
│   └── tsconfig.json       # TypeScript配置
├── docker/                 # Docker相关文件
│   ├── app/                # 应用代码
│   │   └── app.py          # FastAPI应用
│   ├── Dockerfile          # Docker构建文件
│   └── requirements.txt    # Python依赖
├── scripts/                # 部署脚本
│   └── deploy.sh           # 自动化部署脚本
└── README.md               # 项目说明文档
```

## 技术栈

- **后端框架**：FastAPI
- **Agent框架**：Strands Agents
- **大语言模型**：Amazon Bedrock (Claude)
- **容器化**：Docker
- **基础设施即代码**：AWS CDK (TypeScript)
- **数据存储**：Amazon DynamoDB
- **部署环境**：AWS Fargate

## 部署步骤

### 前提条件

- AWS账户和配置好的AWS CLI凭证
- Node.js 18+
- Docker
- Python 3.10+

### 1. 准备环境

克隆项目并安装依赖：

```bash
git clone <repository-url>
cd fund-advisor-fargate
```

### 2. 准备知识库和DynamoDB

```bash
cd scripts
sh deploy_prereqs.sh
```

### 3. 构建和部署CDK堆栈

```bash
cd ../cdk
npm install
npm run build
cdk deploy
```

### 4. 一键部署（可选）

使用自动化部署脚本：

```bash
cd ../scripts
sh deploy.sh
```

### 5. 验证部署

```bash
# 获取API端点
aws cloudformation describe-stacks --stack-name FundAdvisorFargateStack --query "Stacks[0].Outputs[?OutputKey=='FundAdvisorServiceEndpoint'].OutputValue" --output text

# 测试API
curl -X POST http://<endpoint>/advisor -H "Content-Type: application/json" -d '{"query":"推荐一些低风险基金"}'
```

## API参考

### 同步API

**端点**: `/advisor`  
**方法**: POST  
**请求体**:
```json
{
  "query": "推荐一些低风险基金",
  "session_id": "optional-session-id"
}
```
**响应**:
```json
{
  "response": "基于您的需求，以下是几只低风险基金推荐：...",
  "session_id": "session-id",
  "status": "success"
}
```

### 流式API

**端点**: `/advisor/stream`  
**方法**: POST  
**请求体**: 同上  
**响应**: 文本流，逐步返回响应内容

## 性能优化

本项目在Fargate部署中进行了以下性能优化：

1. **资源分配**：根据Agent复杂度调整任务CPU和内存
2. **模型缓存**：缓存常用的模型响应
3. **异步处理**：对于复杂查询，使用异步处理机制
4. **负载均衡**：使用Application Load Balancer分发请求
5. **自动扩展**：基于CPU利用率和请求数量自动扩展容器实例

## 安全考虑

1. **IAM权限最小化**：仅授予必要的权限
2. **敏感信息管理**：使用AWS Secrets Manager存储API密钥
3. **网络安全**：使用私有子网和安全组限制访问
4. **非root用户**：容器内使用非特权用户运行应用
5. **日志监控**：配置CloudWatch日志和告警

## 监控和日志

- **CloudWatch指标**：监控容器CPU、内存使用率
- **应用日志**：结构化日志输出到CloudWatch Logs
- **告警设置**：关键指标超阈值时触发告警
- **健康检查**：ALB定期检查应用健康状态

## 扩展和优化建议

1. **添加API网关**：为API添加认证、限流和缓存
2. **实现WebSocket**：支持实时交互体验
3. **添加CDN**：使用CloudFront加速静态资源
4. **自动扩展策略优化**：基于预测模型进行主动扩展
5. **蓝绿部署**：实现零停机更新

## 故障排除

### 常见问题

1. **部署失败**
   - 检查AWS凭证是否有效
   - 确认IAM权限是否足够
   - 查看CloudFormation事件日志

2. **容器启动失败**
   - 检查Docker构建是否成功
   - 查看ECS任务日志
   - 验证内存和CPU配置是否足够

3. **API响应错误**
   - 检查健康检查是否通过
   - 查看应用日志中的错误信息
   - 验证Bedrock模型访问权限

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