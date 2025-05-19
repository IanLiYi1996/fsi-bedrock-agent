import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as path from 'path';
import { bedrock } from '@cdklabs/generative-ai-cdk-constructs';

/**
 * 投资组合管理Agent构造
 * 创建投资组合管理Agent作为主管理者，使用自定义编排协调多个Agent
 */
export class PortfolioManager extends Construct {
  public readonly portfolioManagerAgent: bedrock.Agent;
  public readonly portfolioManagerAgentAlias: bedrock.AgentAlias;
  public readonly orchestrationFunction: lambda.Function;

  constructor(scope: Construct, id: string, props: PortfolioManagerProps) {
    super(scope, id);

    // 创建自定义编排Lambda函数
    this.orchestrationFunction = new lambda.Function(this, 'OrchestrationFunction', {
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: 'index.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../lambda/orchestration')),
    });

    // 创建投资组合管理Agent作为主管理者
    this.portfolioManagerAgent = new bedrock.Agent(this, 'PortfolioManagerAgent', {
      name: 'PortfolioManagerAgent',
      instruction: '你是投资组合管理者，负责整合各专家意见和分析结果，并做出最终交易决策。你会权衡不同投资专家的观点、技术和基本面分析结果，以及风险评估，为每只股票制定最佳投资策略。你的决策应该考虑投资目标、风险承受能力和市场环境。',
      foundationModel: bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
      knowledgeBases: [props.knowledgeBase],
      userInputEnabled: true,
      shouldPrepareAgent: true,
      customOrchestration: {
        executor: bedrock.OrchestrationExecutor.fromlambdaFunction(this.orchestrationFunction),
      },
      orchestrationType: bedrock.OrchestrationType.CUSTOM_ORCHESTRATION,
    });

    // 创建投资组合管理Agent别名
    this.portfolioManagerAgentAlias = new bedrock.AgentAlias(this, 'PortfolioManagerAgentAlias', {
      agent: this.portfolioManagerAgent,
      aliasName: 'production',
    });

    // 设置环境变量，供自定义编排Lambda使用
    this.orchestrationFunction.addEnvironment('WARREN_BUFFETT_AGENT_ALIAS_ID', props.expertAgents.buffettAgentAlias.aliasId || '');
    this.orchestrationFunction.addEnvironment('BILL_ACKMAN_AGENT_ALIAS_ID', props.expertAgents.ackmanAgentAlias.aliasId || '');
    this.orchestrationFunction.addEnvironment('CHARLIE_MUNGER_AGENT_ALIAS_ID', props.expertAgents.mungerAgentAlias.aliasId || '');
    this.orchestrationFunction.addEnvironment('VALUATION_AGENT_ALIAS_ID', props.analysisAgents.valuationAgentAlias.aliasId || '');
    this.orchestrationFunction.addEnvironment('SENTIMENT_AGENT_ALIAS_ID', props.analysisAgents.sentimentAgentAlias.aliasId || '');
    this.orchestrationFunction.addEnvironment('FUNDAMENTALS_AGENT_ALIAS_ID', props.analysisAgents.fundamentalsAgentAlias.aliasId || '');
    this.orchestrationFunction.addEnvironment('TECHNICALS_AGENT_ALIAS_ID', props.analysisAgents.technicalsAgentAlias.aliasId || '');
    this.orchestrationFunction.addEnvironment('RISK_MANAGER_AGENT_ALIAS_ID', props.analysisAgents.riskManagerAgentAlias.aliasId || '');

    // 授予Lambda函数调用其他Agent的权限
    props.expertAgents.buffettAgentAlias.grantInvoke(this.orchestrationFunction);
    props.expertAgents.ackmanAgentAlias.grantInvoke(this.orchestrationFunction);
    props.expertAgents.mungerAgentAlias.grantInvoke(this.orchestrationFunction);
    props.analysisAgents.valuationAgentAlias.grantInvoke(this.orchestrationFunction);
    props.analysisAgents.sentimentAgentAlias.grantInvoke(this.orchestrationFunction);
    props.analysisAgents.fundamentalsAgentAlias.grantInvoke(this.orchestrationFunction);
    props.analysisAgents.technicalsAgentAlias.grantInvoke(this.orchestrationFunction);
    props.analysisAgents.riskManagerAgentAlias.grantInvoke(this.orchestrationFunction);
  }
}

/**
 * 投资组合管理Agent构造属性
 */
export interface PortfolioManagerProps {
  /**
   * 金融知识库
   */
  readonly knowledgeBase: bedrock.IKnowledgeBase;

  /**
   * 投资专家Agent
   */
  readonly expertAgents: {
    buffettAgentAlias: bedrock.AgentAlias;
    ackmanAgentAlias: bedrock.AgentAlias;
    mungerAgentAlias: bedrock.AgentAlias;
  };

  /**
   * 分析Agent
   */
  readonly analysisAgents: {
    valuationAgentAlias: bedrock.AgentAlias;
    sentimentAgentAlias: bedrock.AgentAlias;
    fundamentalsAgentAlias: bedrock.AgentAlias;
    technicalsAgentAlias: bedrock.AgentAlias;
    riskManagerAgentAlias: bedrock.AgentAlias;
  };
}