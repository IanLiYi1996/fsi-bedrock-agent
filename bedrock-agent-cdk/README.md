# Bedrock Agent CDK 项目

这个项目使用AWS CDK和TypeScript创建Amazon Bedrock Agent。该项目展示了如何使用`@cdklabs/generative-ai-cdk-constructs`库来创建和配置Bedrock Agent，包括添加Action Group、创建Agent别名等功能。

## 项目结构

```
bedrock-agent-cdk/
├── bin/                    # CDK应用程序入口
│   └── bedrock-agent-app.ts
├── lib/                    # CDK堆栈定义
│   └── bedrock-agent-stack.ts
├── lambda/                 # Lambda函数代码
│   └── action-group/
│       └── index.js        # Action Group处理函数
├── cdk.json                # CDK配置
├── package.json            # 项目依赖
└── tsconfig.json           # TypeScript配置
```

## 功能特点

- 创建基本的Bedrock Agent，使用Claude 3.5 Sonnet作为基础模型
- 配置Agent的指令和用户输入设置
- 创建Lambda函数作为Action Group的执行器
- 定义Action Group的API Schema
- 创建Agent别名用于部署
- 输出Agent和Agent别名的ARN

## 前提条件

- Node.js (v14.x或更高版本)
- AWS CLI已配置
- AWS CDK已安装
- AWS账户中已启用Amazon Bedrock服务和相应的模型访问权限

## 安装

1. 克隆此仓库
2. 安装依赖

```bash
cd bedrock-agent-cdk
npm install
```

## 部署

1. 引导CDK环境（如果这是您第一次在此AWS账户/区域中使用CDK）

```bash
npm run bootstrap
```

2. 构建项目

```bash
npm run build
```

3. 部署堆栈

```bash
npm run deploy
```

## 使用方法

部署完成后，您可以在AWS控制台中查看创建的Bedrock Agent。您可以通过以下方式与Agent交互：

1. 在Amazon Bedrock控制台中测试Agent
2. 使用AWS SDK调用Agent API
3. 集成到您的应用程序中

## 自定义

您可以通过修改`lib/bedrock-agent-stack.ts`文件来自定义Agent的配置：

- 更改基础模型
- 修改Agent指令
- 添加知识库
- 配置记忆功能
- 添加更多Action Group
- 设置Agent协作

## 扩展

您可以通过以下方式扩展此项目：

1. 添加知识库集成
2. 实现自定义编排
3. 配置Agent记忆
4. 添加更多Action Group
5. 设置Agent协作

## 清理

要删除部署的资源，请运行：

```bash
npm run cdk destroy
```

## 参考资料

- [Amazon Bedrock文档](https://docs.aws.amazon.com/bedrock/)
- [AWS CDK文档](https://docs.aws.amazon.com/cdk/)
- [Generative AI CDK Constructs](https://github.com/awslabs/generative-ai-cdk-constructs)
