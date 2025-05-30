import { Construct } from 'constructs';
import { bedrock } from '@cdklabs/generative-ai-cdk-constructs';

/**
 * 分析Agent构造
 * 创建多个分析Agent，负责分析基金的不同方面，并提供专业的分析结果
 */
export class AnalysisAgents extends Construct {
  public readonly performanceAgentAlias: bedrock.AgentAlias;
  public readonly holdingsAgentAlias: bedrock.AgentAlias;
  public readonly managerAgentAlias: bedrock.AgentAlias;
  public readonly feesAgentAlias: bedrock.AgentAlias;

  constructor(scope: Construct, id: string, props: AnalysisAgentsProps) {
    super(scope, id);

    // 基金业绩分析Agent
    const performanceAgent = new bedrock.Agent(this, 'PerformanceAgent', {
      name: 'PerformanceAgent',
      instruction: `你是基金业绩分析专家，负责分析基金的历史业绩、波动性和风险调整收益。
你需要评估基金在不同时间段的表现、与基准的对比以及风险调整后的收益指标。
当分析基金时，你应该关注年化收益率、最大回撤、夏普比率、信息比率等关键指标。

分析要点：
1. 基金在不同时间段（1月、3月、6月、1年、3年、5年）的收益表现
2. 基金与业绩比较基准的对比
3. 基金的波动性指标（标准差、最大回撤）
4. 风险调整收益指标（夏普比率、信息比率、特雷诺比率）
5. 基金在不同市场环境下的表现一致性

你的分析应该客观、全面，并提供具体的数据支持。`,
      foundationModel: bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
      knowledgeBases: [props.knowledgeBase],
    });

    // 持仓分析Agent
    const holdingsAgent = new bedrock.Agent(this, 'HoldingsAgent', {
      name: 'HoldingsAgent',
      instruction: `你是基金持仓分析专家，负责分析基金的持仓结构、行业分布和重仓股。
你需要评估基金的持仓集中度、行业配置和个股选择。
当分析基金时，你应该关注前十大重仓股、行业分布比例、持仓变动趋势和潜在风险暴露。

分析要点：
1. 基金的前十大重仓股及其占比
2. 基金的行业配置分布及其与基准的偏离度
3. 基金持仓的集中度和分散度
4. 重仓股的质量和潜在风险
5. 持仓变动趋势及其反映的投资策略变化

你的分析应该深入、专业，帮助投资者理解基金的实际投资方向和风格。`,
      foundationModel: bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
      knowledgeBases: [props.knowledgeBase],
    });

    // 基金经理分析Agent
    const managerAgent = new bedrock.Agent(this, 'ManagerAgent', {
      name: 'ManagerAgent',
      instruction: `你是基金经理分析专家，负责评估基金经理的投资风格、历史业绩和管理能力。
你需要分析基金经理的从业经历、管理业绩和投资理念。
当分析基金经理时，你应该关注其从业年限、历史管理业绩、投资风格一致性和团队稳定性。

分析要点：
1. 基金经理的从业经历和专业背景
2. 基金经理的历史管理业绩和业绩稳定性
3. 基金经理的投资风格和理念
4. 基金经理的团队构成和稳定性
5. 基金经理在不同市场环境下的表现

你的分析应该全面评估基金经理的能力和风格，帮助投资者了解基金背后的管理团队。`,
      foundationModel: bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
      knowledgeBases: [props.knowledgeBase],
    });

    // 费用分析Agent
    const feesAgent = new bedrock.Agent(this, 'FeesAgent', {
      name: 'FeesAgent',
      instruction: `你是基金费用分析专家，负责分析基金的各项费用及其对长期收益的影响。
你需要评估基金的管理费、托管费、申购赎回费等各项费用结构。
当分析基金费用时，你应该关注费率水平、费用对长期收益的影响以及与同类基金的费率比较。

分析要点：
1. 基金的管理费率和托管费率
2. 基金的申购费率和赎回费率结构
3. 基金的销售服务费和其他费用
4. 费用对基金长期收益的影响测算
5. 与同类基金的费率比较

你的分析应该帮助投资者理解基金费用结构，评估费用的合理性和对长期收益的影响。`,
      foundationModel: bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
      knowledgeBases: [props.knowledgeBase],
    });

    // 创建Agent别名
    this.performanceAgentAlias = new bedrock.AgentAlias(this, 'PerformanceAgentAlias', {
      agent: performanceAgent,
      aliasName: 'production',
    });

    this.holdingsAgentAlias = new bedrock.AgentAlias(this, 'HoldingsAgentAlias', {
      agent: holdingsAgent,
      aliasName: 'production',
    });

    this.managerAgentAlias = new bedrock.AgentAlias(this, 'ManagerAgentAlias', {
      agent: managerAgent,
      aliasName: 'production',
    });

    this.feesAgentAlias = new bedrock.AgentAlias(this, 'FeesAgentAlias', {
      agent: feesAgent,
      aliasName: 'production',
    });
  }
}

/**
 * 分析Agent构造属性
 */
export interface AnalysisAgentsProps {
  /**
   * 基金知识库
   */
  readonly knowledgeBase: bedrock.IKnowledgeBase;
}