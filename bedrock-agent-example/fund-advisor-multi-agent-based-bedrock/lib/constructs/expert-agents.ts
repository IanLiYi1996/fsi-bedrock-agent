import { Construct } from 'constructs';
import { bedrock } from '@cdklabs/generative-ai-cdk-constructs';

/**
 * 专家Agent构造
 * 创建多个投资专家Agent，每个专家Agent都有自己的专业知识和投资风格
 */
export class ExpertAgents extends Construct {
  public readonly fundStrategyAgentAlias: bedrock.AgentAlias;
  public readonly assetAllocationAgentAlias: bedrock.AgentAlias;
  public readonly marketTrendAgentAlias: bedrock.AgentAlias;

  constructor(scope: Construct, id: string, props: ExpertAgentsProps) {
    super(scope, id);

    // 基金策略专家Agent
    const fundStrategyAgent = new bedrock.Agent(this, 'FundStrategyAgent', {
      name: 'FundStrategyAgent',
      instruction: `你是基金策略专家，擅长分析不同基金的投资策略和风格。
你需要评估基金的投资理念、策略执行一致性和适应市场变化的能力。
当分析基金时，你应该关注基金的投资风格、选股策略、行业配置和投资周期表现。

分析要点：
1. 基金的投资策略是否清晰明确
2. 基金经理是否严格执行既定策略
3. 策略在不同市场环境下的适应性
4. 投资风格的一致性和漂移情况
5. 选股策略的有效性和独特性

你的分析应该客观、专业，并提供具体的数据支持。`,
      foundationModel: bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
      knowledgeBases: [props.knowledgeBase],
    });

    // 资产配置专家Agent
    const assetAllocationAgent = new bedrock.Agent(this, 'AssetAllocationAgent', {
      name: 'AssetAllocationAgent',
      instruction: `你是资产配置专家，专注于资产配置和多元化投资组合构建。
你需要评估基金在整体投资组合中的适用性，考虑相关性、分散化效果和风险贡献。
当分析基金时，你应该关注基金与其他资产类别的相关性、在不同市场环境下的表现和对整体投资组合的贡献。

分析要点：
1. 基金与主要资产类别的相关性
2. 基金在投资组合中的最佳配置比例
3. 基金对投资组合整体风险的贡献
4. 基金在不同经济周期中的表现
5. 基金与其他基金的互补性

你的建议应该考虑投资者的整体资产配置需求，而不仅仅是单只基金的表现。`,
      foundationModel: bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
      knowledgeBases: [props.knowledgeBase],
    });

    // 市场趋势专家Agent
    const marketTrendAgent = new bedrock.Agent(this, 'MarketTrendAgent', {
      name: 'MarketTrendAgent',
      instruction: `你是市场趋势专家，分析宏观经济和市场趋势对基金的影响。
你需要评估当前和未来市场环境对不同类型基金的潜在影响。
当分析基金时，你应该关注经济周期、利率环境、行业轮动和市场风格转换对基金表现的影响。

分析要点：
1. 当前宏观经济环境对基金的影响
2. 利率变化趋势对基金的潜在影响
3. 行业轮动对基金持仓的影响
4. 市场风格（成长vs价值、大盘vs小盘）转换的影响
5. 地缘政治和政策变化的潜在影响

你的分析应该前瞻性，帮助投资者理解市场环境变化对基金表现的影响。`,
      foundationModel: bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
      knowledgeBases: [props.knowledgeBase],
    });

    // 创建Agent别名
    this.fundStrategyAgentAlias = new bedrock.AgentAlias(this, 'FundStrategyAgentAlias', {
      agent: fundStrategyAgent,
      aliasName: 'production',
    });

    this.assetAllocationAgentAlias = new bedrock.AgentAlias(this, 'AssetAllocationAgentAlias', {
      agent: assetAllocationAgent,
      aliasName: 'production',
    });

    this.marketTrendAgentAlias = new bedrock.AgentAlias(this, 'MarketTrendAgentAlias', {
      agent: marketTrendAgent,
      aliasName: 'production',
    });
  }
}

/**
 * 专家Agent构造属性
 */
export interface ExpertAgentsProps {
  /**
   * 基金知识库
   */
  readonly knowledgeBase: bedrock.IKnowledgeBase;
}