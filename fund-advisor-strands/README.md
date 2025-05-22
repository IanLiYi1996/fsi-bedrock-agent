# 基金投顾多Agent系统 (Strands Agents实现)

基于Strands Agents框架实现的基金投顾多Agent系统。该系统使用多个专业Agent协作，为用户提供基金分析和推荐服务。

## 系统架构

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

6. **基金数据工具** - 提供基金价格、持仓信息、业绩数据和费用结构

7. **基金知识库** - 提供基金投资知识和市场数据

## 项目结构

```
fund-advisor-strands/
├── __init__.py
├── main.py                  # 主程序入口
├── requirements.txt         # 项目依赖
├── README.md                # 项目说明
├── agents/                  # Agent实现
│   ├── __init__.py
│   ├── portfolio_manager.py # 投资组合管理Agent
│   ├── expert_agents.py     # 专家Agent
│   ├── analysis_agents.py   # 分析Agent
│   ├── user_profile.py      # 用户画像Agent
│   └── fund_selector.py     # 基金筛选Agent
├── tools/                   # 工具实现
│   ├── __init__.py
│   ├── fund_data.py         # 基金数据工具
│   └── fund_search.py       # 基金搜索工具
└── knowledge/               # 知识库资源
    ├── __init__.py
    └── fund_knowledge.py    # 基金知识库管理
```

## 安装与设置

### 前提条件

- Python 3.10+
- AWS账户（用于访问Amazon Bedrock）

### 安装步骤

1. 克隆仓库：
   ```bash
   git clone https://github.com/yourusername/fund-advisor-strands.git
   cd fund-advisor-strands
   ```

2. 创建并激活虚拟环境：
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # 在Windows上使用: .venv\Scripts\activate
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

4. 配置AWS凭证：
   - 设置环境变量：`AWS_ACCESS_KEY_ID`、`AWS_SECRET_ACCESS_KEY`
   - 或使用AWS CLI配置：`aws configure`

## 使用方法

运行主程序：

```bash
python -u main.py
```

系统将启动交互式命令行界面，您可以：

1. 分析特定基金：
   ```
   分析基金000001
   ```

2. 获取基金推荐：
   ```
   我是一个风险偏好中等、投资期限3-5年、偏好科技行业的投资者，请推荐适合我的基金
   ```

## 系统工作流程

### 1. 基金分析流程

1. 用户提供基金代码或名称
2. 投资组合管理Agent接收请求并启动分析流程
3. 调用基金数据工具获取基金基本信息和持仓数据
4. 分别调用各个分析Agent进行专项分析
5. 调用专家Agent获取专业意见
6. 投资组合管理Agent整合所有分析结果，生成综合评估报告和持仓建议

### 2. 基金推荐流程

1. 用户提供投资偏好（风险偏好、投资期限、偏好行业或主题等）
2. 用户画像Agent分析用户需求并建立投资画像
3. 基金筛选Agent根据用户画像筛选符合条件的基金
4. 调用各分析Agent对筛选出的基金进行评估
5. 调用专家Agent对筛选结果提供专业意见
6. 投资组合管理Agent整合分析结果，生成个性化基金推荐列表

## 许可证

MIT
