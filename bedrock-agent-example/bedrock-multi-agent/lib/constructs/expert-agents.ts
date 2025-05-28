import { Construct } from 'constructs';
import { bedrock } from '@cdklabs/generative-ai-cdk-constructs';

/**
 * 投资专家Agent构造
 * 创建多个投资专家Agent，如Warren Buffett、Bill Ackman和Charlie Munger
 */
export class ExpertAgents extends Construct {
  public readonly buffettAgent: bedrock.Agent;
  public readonly ackmanAgent: bedrock.Agent;
  public readonly mungerAgent: bedrock.Agent;
  
  public readonly buffettAgentAlias: bedrock.AgentAlias;
  public readonly ackmanAgentAlias: bedrock.AgentAlias;
  public readonly mungerAgentAlias: bedrock.AgentAlias;

  constructor(scope: Construct, id: string, props: ExpertAgentsProps) {
    super(scope, id);

    // 1. Warren Buffett Agent
    this.buffettAgent = new bedrock.Agent(this, 'WarrenBuffettAgent', {
      name: 'WarrenBuffettAgent',
      instruction: '你是Warren Buffett，奥马哈的先知，伯克希尔·哈撒韦公司的CEO。你寻找具有持久竞争优势的优质公司，以合理价格购买并长期持有。你关注公司的内在价值、管理质量、行业地位和长期增长潜力。你避免不了解的行业，坚持在能力圈内投资。分析股票时，你会考虑公司的护城河、盈利能力、资本回报率和管理层诚信。',
      foundationModel: bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
      knowledgeBases: [props.knowledgeBase],
      userInputEnabled: true,
      shouldPrepareAgent: true,
    });

    // 2. Bill Ackman Agent
    this.ackmanAgent = new bedrock.Agent(this, 'BillAckmanAgent', {
      name: 'BillAckmanAgent',
      instruction: '你是Bill Ackman，潘兴广场资本管理公司的创始人和CEO。你是一位积极投资者，寻找可以推动变革的公司。你关注简单、可预测的现金流业务，并愿意采取激进立场推动管理层改变。你进行深入研究，寻找被低估的优质企业，并通过公开倡导、董事会席位或管理层变更来创造价值。分析股票时，你会考虑公司治理、资本配置、运营效率和战略定位。',
      foundationModel: bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
      knowledgeBases: [props.knowledgeBase],
      userInputEnabled: true,
      shouldPrepareAgent: true,
    });

    // 3. Charlie Munger Agent
    this.mungerAgent = new bedrock.Agent(this, 'CharlieMongerAgent', {
      name: 'CharlieMongerAgent',
      instruction: '你是Charlie Munger，伯克希尔·哈撒韦公司的副主席。你强调多学科思维模型和避免愚蠢错误的重要性。你寻找具有良好经济特性的优质企业，由诚实且能干的管理层经营。你相信"以合理价格购买优质企业，而不是以便宜价格购买平庸企业"。分析股票时，你会考虑商业模式的质量、竞争优势的持久性、管理层的诚信和能力，以及估值的合理性。',
      foundationModel: bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
      knowledgeBases: [props.knowledgeBase],
      userInputEnabled: true,
      shouldPrepareAgent: true,
    });

    // 创建Agent别名
    this.buffettAgentAlias = new bedrock.AgentAlias(this, 'BuffettAgentAlias', {
      agent: this.buffettAgent,
      aliasName: 'production',
    });

    this.ackmanAgentAlias = new bedrock.AgentAlias(this, 'AckmanAgentAlias', {
      agent: this.ackmanAgent,
      aliasName: 'production',
    });

    this.mungerAgentAlias = new bedrock.AgentAlias(this, 'MungerAgentAlias', {
      agent: this.mungerAgent,
      aliasName: 'production',
    });
  }
}

/**
 * 投资专家Agent构造属性
 */
export interface ExpertAgentsProps {
  /**
   * 金融知识库
   */
  readonly knowledgeBase: bedrock.IKnowledgeBase;
}