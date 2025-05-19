import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as path from 'path';
import * as fs from 'fs';
import { bedrock } from '@cdklabs/generative-ai-cdk-constructs';

/**
 * 分析Agent构造
 * 创建多个分析Agent，如估值、情绪、基本面和技术面分析
 */
export class AnalysisAgents extends Construct {
  public readonly valuationAgent: bedrock.Agent;
  public readonly sentimentAgent: bedrock.Agent;
  public readonly fundamentalsAgent: bedrock.Agent;
  public readonly technicalsAgent: bedrock.Agent;
  public readonly riskManagerAgent: bedrock.Agent;
  
  public readonly valuationAgentAlias: bedrock.AgentAlias;
  public readonly sentimentAgentAlias: bedrock.AgentAlias;
  public readonly fundamentalsAgentAlias: bedrock.AgentAlias;
  public readonly technicalsAgentAlias: bedrock.AgentAlias;
  public readonly riskManagerAgentAlias: bedrock.AgentAlias;
  
  public readonly financialDataActionGroup: bedrock.AgentActionGroup;

  constructor(scope: Construct, id: string, props: AnalysisAgentsProps) {
    super(scope, id);

    // 创建金融数据Action Group的Lambda函数
    const financialDataFunction = new lambda.Function(this, 'FinancialDataFunction', {
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: 'index.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../lambda/financial-data')),
    });

    // 创建金融数据Action Group
    const schemaPath = path.join(__dirname, '../../config/api-schemas/financial-data-schema.json');
    const schemaContent = fs.readFileSync(schemaPath, 'utf8');
    
    this.financialDataActionGroup = new bedrock.AgentActionGroup({
      name: 'financial-data',
      description: '获取股票的财务数据、价格历史和市场指标',
      executor: bedrock.ActionGroupExecutor.fromlambdaFunction(financialDataFunction),
      apiSchema: bedrock.ApiSchema.fromInline(schemaContent),
    });

    // 1. 估值Agent
    this.valuationAgent = new bedrock.Agent(this, 'ValuationAgent', {
      name: 'ValuationAgent',
      instruction: '你是估值专家，负责计算股票内在价值并生成交易信号。你使用多种估值方法，包括贴现现金流(DCF)、市盈率(P/E)、市净率(P/B)、EV/EBITDA等。你会分析公司的财务报表、增长率、资本回报率和风险因素，以确定股票是被高估还是低估。你的输出应该包括估值结果、使用的方法、关键假设和交易建议。',
      foundationModel: bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
      knowledgeBases: [props.knowledgeBase],
      userInputEnabled: true,
      shouldPrepareAgent: true,
    });

    // 2. 情绪Agent
    this.sentimentAgent = new bedrock.Agent(this, 'SentimentAgent', {
      name: 'SentimentAgent',
      instruction: '你是情绪分析专家，负责分析市场情绪并生成交易信号。你分析新闻报道、社交媒体、分析师评级和市场指标，以评估投资者对特定股票或整体市场的情绪。你会考虑情绪指标如恐惧与贪婪指数、看涨/看跌比率、交易量和波动性。你的输出应该包括情绪评分、关键情绪驱动因素和交易建议。',
      foundationModel: bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
      knowledgeBases: [props.knowledgeBase],
      userInputEnabled: true,
      shouldPrepareAgent: true,
    });

    // 3. 基本面Agent
    this.fundamentalsAgent = new bedrock.Agent(this, 'FundamentalsAgent', {
      name: 'FundamentalsAgent',
      instruction: '你是基本面分析专家，负责分析公司财务健康状况并生成交易信号。你分析收入增长、利润率、资产负债表强度、现金流和资本回报率等指标。你还会考虑行业趋势、竞争地位、管理质量和长期增长前景。你的输出应该包括基本面评估、关键财务指标分析和交易建议。',
      foundationModel: bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
      knowledgeBases: [props.knowledgeBase],
      userInputEnabled: true,
      shouldPrepareAgent: true,
    });

    // 4. 技术面Agent
    this.technicalsAgent = new bedrock.Agent(this, 'TechnicalsAgent', {
      name: 'TechnicalsAgent',
      instruction: '你是技术分析专家，负责分析价格图表和技术指标并生成交易信号。你使用移动平均线、相对强弱指标(RSI)、MACD、布林带和支撑/阻力位等工具。你识别趋势、反转模式、动量和交易量变化。你的输出应该包括技术分析结果、关键技术指标和交易建议。',
      foundationModel: bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
      knowledgeBases: [props.knowledgeBase],
      userInputEnabled: true,
      shouldPrepareAgent: true,
    });

    // 5. 风险管理Agent
    this.riskManagerAgent = new bedrock.Agent(this, 'RiskManagerAgent', {
      name: 'RiskManagerAgent',
      instruction: '你是风险管理专家，负责评估投资风险并设置头寸限制。你分析市场风险、特定股票风险、波动性、流动性和相关性。你计算风险指标如贝塔系数、夏普比率、最大回撤和风险价值(VaR)。你的输出应该包括风险评估、建议的头寸规模和风险缓解策略。',
      foundationModel: bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
      knowledgeBases: [props.knowledgeBase],
      userInputEnabled: true,
      shouldPrepareAgent: true,
    });

    // 为所有分析Agent添加金融数据Action Group
    this.valuationAgent.addActionGroup(this.financialDataActionGroup);
    this.sentimentAgent.addActionGroup(this.financialDataActionGroup);
    this.fundamentalsAgent.addActionGroup(this.financialDataActionGroup);
    this.technicalsAgent.addActionGroup(this.financialDataActionGroup);
    this.riskManagerAgent.addActionGroup(this.financialDataActionGroup);

    // 创建Agent别名
    this.valuationAgentAlias = new bedrock.AgentAlias(this, 'ValuationAgentAlias', {
      agent: this.valuationAgent,
      aliasName: 'production',
    });

    this.sentimentAgentAlias = new bedrock.AgentAlias(this, 'SentimentAgentAlias', {
      agent: this.sentimentAgent,
      aliasName: 'production',
    });

    this.fundamentalsAgentAlias = new bedrock.AgentAlias(this, 'FundamentalsAgentAlias', {
      agent: this.fundamentalsAgent,
      aliasName: 'production',
    });

    this.technicalsAgentAlias = new bedrock.AgentAlias(this, 'TechnicalsAgentAlias', {
      agent: this.technicalsAgent,
      aliasName: 'production',
    });

    this.riskManagerAgentAlias = new bedrock.AgentAlias(this, 'RiskManagerAgentAlias', {
      agent: this.riskManagerAgent,
      aliasName: 'production',
    });
  }
}

/**
 * 分析Agent构造属性
 */
export interface AnalysisAgentsProps {
  /**
   * 金融知识库
   */
  readonly knowledgeBase: bedrock.IKnowledgeBase;
}