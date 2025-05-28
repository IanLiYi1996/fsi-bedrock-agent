import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as path from 'path';
import * as iam from 'aws-cdk-lib/aws-iam';
import { bedrock } from '@cdklabs/generative-ai-cdk-constructs';

/**
 * 投资组合管理Agent构造
 * 创建投资组合管理Agent作为主管理者，协调多个Agent的工作
 */
export class PortfolioManager extends Construct {
  public readonly portfolioManagerAgent: bedrock.Agent;
  public readonly portfolioManagerAgentAlias: bedrock.AgentAlias;
  public readonly orchestrationFunction: lambda.Function;

  constructor(scope: Construct, id: string, props: PortfolioManagerProps) {
    super(scope, id);

    // 创建编排Lambda函数
    this.orchestrationFunction = new lambda.Function(this, 'OrchestrationFunction', {
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: 'index.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../lambda/orchestration')),
    });

    // 创建投资组合管理Agent
    this.portfolioManagerAgent = new bedrock.Agent(this, 'PortfolioManagerAgent', {
      name: 'PortfolioManagerAgent',
      instruction: `你是基金投资组合管理者，负责整合各专家意见和分析结果，并为用户提供基金投资建议。
你有两个主要职责：
1. 分析用户提供的基金，评估其投资价值和风险，提供持仓建议
2. 根据用户的投资偏好，推荐合适的基金产品

当用户提供基金代码或名称时，你应该分析该基金并提供全面的投资建议。
当用户提供投资偏好时，你应该推荐符合其需求的基金产品。

你的建议应该考虑用户的投资目标、风险承受能力和市场环境。你需要整合各个专家Agent和分析Agent的意见，形成全面、客观的投资建议。`,
      foundationModel: bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
      knowledgeBases: [props.knowledgeBase],
      userInputEnabled: true,
      shouldPrepareAgent: true,
    });

    // 创建投资组合管理Agent别名
    this.portfolioManagerAgentAlias = new bedrock.AgentAlias(this, 'PortfolioManagerAgentAlias', {
      agent: this.portfolioManagerAgent,
      aliasName: 'production',
    });

    // 为投资组合管理Agent添加Action Group
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
          '/analyzeFund': {
            post: {
              operationId: 'analyzeFund',
              summary: '分析基金',
              description: '调用多个专家Agent分析指定的基金',
              requestBody: {
                required: true,
                content: {
                  'application/json': {
                    schema: {
                      type: 'object',
                      required: ['fundCode'],
                      properties: {
                        fundCode: {
                          type: 'string',
                          description: '基金代码'
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
          },
          '/recommendFunds': {
            post: {
              operationId: 'recommendFunds',
              summary: '推荐基金',
              description: '根据用户偏好推荐基金',
              requestBody: {
                required: true,
                content: {
                  'application/json': {
                    schema: {
                      type: 'object',
                      properties: {
                        riskPreference: {
                          type: 'string',
                          description: '风险偏好'
                        },
                        investmentHorizon: {
                          type: 'string',
                          description: '投资期限'
                        },
                        preferredIndustry: {
                          type: 'string',
                          description: '偏好行业'
                        }
                      }
                    }
                  }
                }
              },
              responses: {
                '200': {
                  description: '成功获取推荐结果'
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
    this.orchestrationFunction.addEnvironment('FUND_STRATEGY_AGENT_ALIAS_ID', props.expertAgents.fundStrategyAgentAlias.aliasId || '');
    this.orchestrationFunction.addEnvironment('ASSET_ALLOCATION_AGENT_ALIAS_ID', props.expertAgents.assetAllocationAgentAlias.aliasId || '');
    this.orchestrationFunction.addEnvironment('MARKET_TREND_AGENT_ALIAS_ID', props.expertAgents.marketTrendAgentAlias.aliasId || '');
    
    // 添加分析Agent的Alias ID
    this.orchestrationFunction.addEnvironment('PERFORMANCE_AGENT_ALIAS_ID', props.analysisAgents.performanceAgentAlias.aliasId || '');
    this.orchestrationFunction.addEnvironment('HOLDINGS_AGENT_ALIAS_ID', props.analysisAgents.holdingsAgentAlias.aliasId || '');
    this.orchestrationFunction.addEnvironment('MANAGER_AGENT_ALIAS_ID', props.analysisAgents.managerAgentAlias.aliasId || '');
    this.orchestrationFunction.addEnvironment('FEES_AGENT_ALIAS_ID', props.analysisAgents.feesAgentAlias.aliasId || '');

    // 添加用户画像Agent的Alias ID
    this.orchestrationFunction.addEnvironment('USER_PROFILE_AGENT_ALIAS_ID', props.userProfileAgentAlias.aliasId || '');

    // 添加基金筛选Agent的Alias ID
    this.orchestrationFunction.addEnvironment('FUND_SELECTOR_AGENT_ALIAS_ID', props.fundSelectorAgentAlias.aliasId || '');

    // 授予Lambda函数调用Bedrock Agent的权限
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
    props.expertAgents.fundStrategyAgentAlias.grantInvoke(this.orchestrationFunction);
    props.expertAgents.assetAllocationAgentAlias.grantInvoke(this.orchestrationFunction);
    props.expertAgents.marketTrendAgentAlias.grantInvoke(this.orchestrationFunction);
    props.analysisAgents.performanceAgentAlias.grantInvoke(this.orchestrationFunction);
    props.analysisAgents.holdingsAgentAlias.grantInvoke(this.orchestrationFunction);
    props.analysisAgents.managerAgentAlias.grantInvoke(this.orchestrationFunction);
    props.analysisAgents.feesAgentAlias.grantInvoke(this.orchestrationFunction);
    props.userProfileAgentAlias.grantInvoke(this.orchestrationFunction);
    props.fundSelectorAgentAlias.grantInvoke(this.orchestrationFunction);
  }
}

/**
 * 投资组合管理Agent构造属性
 */
export interface PortfolioManagerProps {
  /**
   * 基金知识库
   */
  readonly knowledgeBase: bedrock.IKnowledgeBase;

  /**
   * 专家Agent
   */
  readonly expertAgents: {
    fundStrategyAgentAlias: bedrock.AgentAlias;
    assetAllocationAgentAlias: bedrock.AgentAlias;
    marketTrendAgentAlias: bedrock.AgentAlias;
  };

  /**
   * 分析Agent
   */
  readonly analysisAgents: {
    performanceAgentAlias: bedrock.AgentAlias;
    holdingsAgentAlias: bedrock.AgentAlias;
    managerAgentAlias: bedrock.AgentAlias;
    feesAgentAlias: bedrock.AgentAlias;
  };

  /**
   * 用户画像Agent
   */
  readonly userProfileAgentAlias: bedrock.AgentAlias;

  /**
   * 基金筛选Agent
   */
  readonly fundSelectorAgentAlias: bedrock.AgentAlias;
}