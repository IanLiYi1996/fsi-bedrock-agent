import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as path from 'path';
import * as iam from 'aws-cdk-lib/aws-iam';
import { bedrock } from '@cdklabs/generative-ai-cdk-constructs';

/**
 * 投资组合管理Agent构造
 * 创建投资组合管理Agent作为主管理者，使用高级提示模板协调多个Agent
 * 注意：根据Amazon Bedrock文档，使用自定义编排的Supervisor agents不支持多Agent协作
 */
export class PortfolioManager extends Construct {
  public readonly portfolioManagerAgent: bedrock.Agent;
  public readonly portfolioManagerAgentAlias: bedrock.AgentAlias;
  public readonly orchestrationFunction: lambda.Function;

  constructor(scope: Construct, id: string, props: PortfolioManagerProps) {
    super(scope, id);

    // 创建辅助Lambda函数，用于处理Agent之间的协作
    this.orchestrationFunction = new lambda.Function(this, 'OrchestrationFunction', {
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: 'index.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../lambda/orchestration')),
    });

    // 创建投资组合管理Agent作为主管理者
    // 注意：不再使用自定义编排，而是使用高级提示模板
    this.portfolioManagerAgent = new bedrock.Agent(this, 'PortfolioManagerAgent', {
      name: 'PortfolioManagerAgent',
      instruction: `你是投资组合管理者，负责整合各专家意见和分析结果，并做出最终交易决策。
你会权衡不同投资专家的观点、技术和基本面分析结果，以及风险评估，为每只股票制定最佳投资策略。
你的决策应该考虑投资目标、风险承受能力和市场环境。
当用户提供股票代码时，你应该分析该股票并提供全面的投资建议。`,
      foundationModel: bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
      knowledgeBases: [props.knowledgeBase],
      userInputEnabled: true,
      shouldPrepareAgent: true,
      // 移除自定义编排配置
      // customOrchestration: {
      //   executor: bedrock.OrchestrationExecutor.fromlambdaFunction(this.orchestrationFunction),
      // },
      // orchestrationType: bedrock.OrchestrationType.CUSTOM_ORCHESTRATION,
    });

    // 创建投资组合管理Agent别名
    this.portfolioManagerAgentAlias = new bedrock.AgentAlias(this, 'PortfolioManagerAgentAlias', {
      agent: this.portfolioManagerAgent,
      aliasName: 'production',
    });

    // 为投资组合管理Agent添加Action Group，用于调用其他Agent
    const agentActionGroup = new bedrock.AgentActionGroup({
      name: 'agent-collaboration',
      description: '调用其他Agent获取分析和建议',
      executor: bedrock.ActionGroupExecutor.fromlambdaFunction(this.orchestrationFunction),
      apiSchema: bedrock.ApiSchema.fromInline(JSON.stringify({
        openapi: '3.0.0',
        info: {
          title: 'Agent Collaboration API',
          version: '1.0.0',
          description: 'API for collaborating with other agents'
        },
        paths: {
          '/analyzeStock': {
            post: {
              operationId: 'analyzeStock',
              summary: '分析股票',
              description: '调用多个专家Agent分析指定的股票',
              requestBody: {
                required: true,
                content: {
                  'application/json': {
                    schema: {
                      type: 'object',
                      required: ['ticker'],
                      properties: {
                        ticker: {
                          type: 'string',
                          description: '股票代码'
                        }
                      }
                    }
                  }
                }
              },
              responses: {
                '200': {
                  description: '成功获取分析结果'
                }
              }
            }
          }
        }
      }))
    });

    // 将Action Group添加到Agent
    this.portfolioManagerAgent.addActionGroup(agentActionGroup);

    // 设置环境变量，供Lambda函数使用
    // 添加专家Agent的Alias ID
    this.orchestrationFunction.addEnvironment('WARREN_BUFFETT_AGENT_ALIAS_ID', props.expertAgents.buffettAgentAlias.aliasId || '');
    this.orchestrationFunction.addEnvironment('BILL_ACKMAN_AGENT_ALIAS_ID', props.expertAgents.ackmanAgentAlias.aliasId || '');
    this.orchestrationFunction.addEnvironment('CHARLIE_MUNGER_AGENT_ALIAS_ID', props.expertAgents.mungerAgentAlias.aliasId || '');
    
    // 添加分析Agent的Alias ID
    this.orchestrationFunction.addEnvironment('VALUATION_AGENT_ALIAS_ID', props.analysisAgents.valuationAgentAlias.aliasId || '');
    this.orchestrationFunction.addEnvironment('SENTIMENT_AGENT_ALIAS_ID', props.analysisAgents.sentimentAgentAlias.aliasId || '');
    this.orchestrationFunction.addEnvironment('FUNDAMENTALS_AGENT_ALIAS_ID', props.analysisAgents.fundamentalsAgentAlias.aliasId || '');
    this.orchestrationFunction.addEnvironment('TECHNICALS_AGENT_ALIAS_ID', props.analysisAgents.technicalsAgentAlias.aliasId || '');
    this.orchestrationFunction.addEnvironment('RISK_MANAGER_AGENT_ALIAS_ID', props.analysisAgents.riskManagerAgentAlias.aliasId || '');

    // 授予Lambda函数调用Bedrock Agent的广泛权限
    const bedrockAgentPolicy = new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        'bedrock:InvokeAgent',
        'bedrock:InvokeModel',
        'bedrock:Retrieve',
        'bedrock:RetrieveAndGenerate'
      ],
      resources: ['*'], // 为简化起见，允许访问所有资源
    });
    
    this.orchestrationFunction.addToRolePolicy(bedrockAgentPolicy);
    
    // 同时保留原有的特定Agent调用权限
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
