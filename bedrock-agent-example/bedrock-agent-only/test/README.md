# 本地测试 Amazon Bedrock Agent

本目录包含用于在本地测试已部署的Amazon Bedrock Agent的工具。

## 前提条件

在开始测试之前，请确保您已经：

1. 部署了Bedrock Agent（通过运行`npm run deploy`）
2. 安装了所有依赖项（通过运行`npm install`）
3. 配置了AWS凭证（通过AWS CLI或环境变量）

## 配置AWS凭证

您需要配置AWS凭证才能访问您的Bedrock Agent。有几种方法可以配置凭证：

### 方法1：使用AWS CLI

如果您已经安装了AWS CLI，可以运行以下命令配置凭证：

```bash
aws configure
```

系统会提示您输入Access Key ID、Secret Access Key、默认区域和输出格式。

### 方法2：设置环境变量

您也可以通过设置环境变量来配置凭证：

```bash
# Linux/macOS
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
export AWS_REGION=us-east-1  # 替换为您的Agent所在区域

# Windows
set AWS_ACCESS_KEY_ID=your_access_key_id
set AWS_SECRET_ACCESS_KEY=your_secret_access_key
set AWS_REGION=us-east-1  # 替换为您的Agent所在区域
```

## 获取Agent别名ID

在测试之前，您需要获取已部署的Agent别名ID。您可以通过以下方式获取：

1. 从CDK部署输出中获取（部署完成后会显示）
2. 从AWS控制台的Bedrock服务中查看
3. 使用AWS CLI命令获取：

```bash
aws bedrock list-agent-aliases --agent-id YOUR_AGENT_ID
```

## 运行测试脚本

使用以下命令运行测试脚本：

```bash
node test-agent.js YOUR_AGENT_ID YOUR_AGENT_ALIAS_ID
```

将`YOUR_AGENT_ID`替换为您的实际Agent ID，将`YOUR_AGENT_ALIAS_ID`替换为您的实际Agent别名ID。

您可以从CDK部署输出或AWS控制台获取这些ID。Agent ID通常是一个以"agent/"开头的ARN的最后一部分，例如"arn:aws:bedrock:us-east-1:123456789012:agent/abcdef123456"中的"abcdef123456"。

## 测试脚本功能

测试脚本提供以下功能：

1. 与您的Bedrock Agent进行交互式对话
2. 显示Agent的响应
3. 显示Agent执行的操作（如果有）
4. 显示Agent的思考过程（如果启用了跟踪）
5. 维护会话状态，使对话具有上下文连续性

## 示例对话

```
使用Agent ID: abcdef123456
使用Agent别名ID: ghijkl789012
开始与Agent对话。输入"exit"退出。
------------------------------
您: 你能告诉我关于战争与和平这本书的信息吗？
正在处理...

机器人: 
我可以为您提供关于《战争与和平》的信息。这是俄国作家列夫·托尔斯泰创作的长篇小说，发表于1869年。这部作品描述了拿破仑入侵俄国期间俄国社会的各个方面。

执行的操作:
- 操作组: query-library
  - 操作: getBookById
    API路径: /books/1
    结果:
    {
      "id": "1",
      "title": "战争与和平",
      "author": "列夫·托尔斯泰",
      "year": 1869,
      "summary": "《战争与和平》是俄国作家列夫·托尔斯泰创作的长篇小说，描述了拿破仑入侵俄国期间俄国社会的各个方面。"
    }

------------------------------
您: exit
对话结束
```

## 故障排除

如果您遇到问题，请检查以下几点：

1. 确保您的AWS凭证有权访问Bedrock服务
2. 确保您使用了正确的Agent别名ID
3. 确保您的Agent已经成功部署并处于活动状态
4. 检查您的网络连接是否可以访问AWS服务
5. 查看AWS CloudWatch日志以获取更详细的错误信息
