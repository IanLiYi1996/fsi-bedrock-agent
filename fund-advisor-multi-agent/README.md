# 基金投顾多Agent系统

基于Amazon Bedrock Agents实现的基金投顾多Agent系统。该系统使用多个专业Agent协作，为用户提供基金分析和推荐服务。

## 系统架构

![系统架构](../assets/pics/fund-advisor.png)

系统包含以下组件：

1. **专家Agent**
   - 基金策略专家Agent - 分析基金的投资策略和风格
   - 资产配置专家Agent - 评估基金在投资组合中的适用性
   - 市场趋势专家Agent - 分析宏观经济和市场趋势对基金的影响

2. **分析Agent**
   - 基金业绩分析Agent - 分析基金历史业绩和风险调整收益
   - 持仓分析Agent - 分析基金的持仓结构和行业分布
   - 基金经理分析Agent - 评估基金经理的投资风格和管理能力
   - 费用分析Agent - 分析基金的费用结构及其对收益的影响

3. **用户画像Agent** - 分析用户的风险偏好、投资目标和投资期限

4. **基金筛选Agent** - 根据用户偏好筛选合适的基金

5. **投资组合管理Agent** - 整合所有分析结果，生成最终的基金投资建议

6. **基金数据Action Group** - 提供基金价格、持仓信息、业绩数据和费用结构

7. **自定义编排Lambda** - 控制多Agent协作流程

8. **基金知识库** - 提供基金投资知识和市场数据

## 项目结构

```
fund-advisor-multi-agent/
├── config/
│   └── api-schemas/
│       └── fund-data-schema.json      # 基金数据API Schema
├── lambda/
│   ├── fund-data/
│   │   └── index.py                   # 基金数据API Lambda函数
│   ├── fund-search/
│   │   └── index.py                   # 基金搜索Lambda函数
│   └── orchestration/
│       └── index.py                   # 自定义编排Lambda函数
└── lib/
    ├── constructs/
    │   ├── knowledge-base.ts          # 基金知识库构造
    │   ├── expert-agents.ts           # 专家Agent构造
    │   ├── analysis-agents.ts         # 分析Agent构造
    │   ├── user-profile-agent.ts      # 用户画像Agent构造
    │   ├── fund-selector-agent.ts     # 基金筛选Agent构造
    │   └── portfolio-manager.ts       # 投资组合管理Agent构造
    └── fund-advisor-stack.ts          # 主堆栈文件
```

## 组件说明

### 1. 基金知识库构造 (knowledge-base.ts)

负责创建S3存储桶和向量知识库，用于存储和检索基金数据。

### 2. 专家Agent构造 (expert-agents.ts)

创建多个投资专家Agent，每个专家Agent都有自己的专业知识和投资风格。

### 3. 分析Agent构造 (analysis-agents.ts)

创建多个分析Agent，负责分析基金的不同方面，并提供专业的分析结果。

### 4. 用户画像Agent构造 (user-profile-agent.ts)

创建用户画像Agent，负责分析用户的风险偏好、投资目标、投资期限和流动性需求。

### 5. 基金筛选Agent构造 (fund-selector-agent.ts)

创建基金筛选Agent，负责根据用户偏好和投资目标筛选合适的基金。

### 6. 投资组合管理Agent构造 (portfolio-manager.ts)

创建投资组合管理Agent作为主管理者，使用自定义编排协调多个Agent。

### 7. 基金数据API Lambda函数 (fund-data/index.py)

提供基金数据API，包括获取基金基本信息、业绩数据、持仓信息、基金经理信息和费用结构。

### 8. 基金搜索Lambda函数 (fund-search/index.py)

提供基金搜索功能，根据用户偏好筛选合适的基金。

### 9. 自定义编排Lambda函数 (orchestration/index.py)

实现自定义编排逻辑，协调多个Agent的工作流程。

## 系统工作流程

### 1. 基金分析流程

1. 用户提供基金代码或名称
2. 投资组合管理Agent接收请求并启动分析流程
3. 调用基金数据Action Group获取基金基本信息和持仓数据
4. 分别调用各个分析Agent进行专项分析：
   - 基金业绩分析Agent评估历史表现
   - 持仓分析Agent分析持仓结构
   - 基金经理分析Agent评估管理能力
   - 费用分析Agent分析成本结构
5. 调用专家Agent获取专业意见：
   - 基金策略专家Agent分析投资策略
   - 资产配置专家Agent评估在投资组合中的适用性
   - 市场趋势专家Agent分析市场环境对该基金的影响
6. 投资组合管理Agent整合所有分析结果，生成综合评估报告和持仓建议

### 2. 基金推荐流程

1. 用户提供投资偏好（风险偏好、投资期限、偏好行业或主题等）
2. 用户画像Agent分析用户需求并建立投资画像
3. 基金筛选Agent根据用户画像筛选符合条件的基金
4. 调用各分析Agent对筛选出的基金进行评估
5. 调用专家Agent对筛选结果提供专业意见
6. 投资组合管理Agent整合分析结果，生成个性化基金推荐列表

## 部署和使用

### 前提条件

- 安装AWS CDK: `npm install -g aws-cdk`
- 配置AWS凭证: `aws configure`

### 部署步骤

1. 安装依赖:
   ```bash
   npm install
   ```

2. 编译TypeScript代码:
   ```bash
   npm run build
   ```

3. 部署堆栈:
   ```bash
   npx cdk deploy
   ```

4. 部署完成后，您将获得投资组合管理Agent的ID和别名ID，可以通过AWS控制台或API调用此Agent。

### 使用示例

部署后，您可以通过AWS控制台或API调用投资组合管理Agent，提供基金代码进行分析或提供投资偏好获取推荐：

```
分析基金000001的投资价值
```

系统将：
1. 调用各个专家Agent获取他们的分析
2. 调用分析Agent获取技术指标
3. 整合所有信息生成最终投资建议

或者：

```
我是一个风险偏好中等、投资期限3-5年、偏好科技行业的投资者，请推荐适合我的基金
```

系统将：
1. 分析用户的投资画像
2. 筛选符合条件的基金
3. 评估筛选结果
4. 生成个性化的基金推荐列表

## 常用命令

* `npm run build`   编译TypeScript代码
* `npm run watch`   监视文件变化并自动编译
* `npm run test`    执行Jest单元测试
* `npx cdk deploy`  部署堆栈到默认AWS账户/区域
* `npx cdk diff`    比较已部署堆栈与当前状态
* `npx cdk synth`   生成CloudFormation模板

## 扩展建议

1. 添加更多专业Agent，如税务规划专家、退休规划专家等
2. 增强基金数据API，连接真实的基金数据源
3. 添加投资组合回测功能，评估推荐组合的历史表现
4. 实现定期监控功能，当基金表现异常时主动提醒用户
5. 增加ESG（环境、社会和治理）分析维度，满足可持续投资需求