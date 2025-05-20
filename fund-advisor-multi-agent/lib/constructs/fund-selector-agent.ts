import { Construct } from 'constructs';
import { bedrock } from '@cdklabs/generative-ai-cdk-constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as path from 'path';
import * as iam from 'aws-cdk-lib/aws-iam';

/**
 * 基金筛选Agent构造
 * 创建基金筛选Agent，负责根据用户偏好和投资目标筛选合适的基金
 */
export class FundSelectorAgent extends Construct {
  public readonly fundSelectorAgentAlias: bedrock.AgentAlias;
  public readonly fundSearchFunction: lambda.Function;

  constructor(scope: Construct, id: string, props: FundSelectorAgentProps) {
    super(scope, id);

    // 创建基金搜索Lambda函数
    this.fundSearchFunction = new lambda.Function(this, 'FundSearchFunction', {
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: 'index.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../lambda/fund-search')),
    });

    // 授予Lambda函数调用Bedrock的权限
    const bedrockPolicy = new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        'bedrock:InvokeModel',
        'bedrock:Retrieve',
        'bedrock:RetrieveAndGenerate'
      ],
      resources: ['*'], // 为简化起见，允许访问所有资源
    });
    
    this.fundSearchFunction.addToRolePolicy(bedrockPolicy);

    // 基金筛选Agent
    const fundSelectorAgent = new bedrock.Agent(this, 'FundSelectorAgent', {
      name: 'FundSelectorAgent',
      instruction: `你是基金筛选专家，负责根据用户偏好和投资目标筛选合适的基金。
你需要考虑基金类型、风险等级、历史业绩和费用结构等多维度因素。
当筛选基金时，你应该根据用户的风险偏好、投资期限和投资目标，找到最匹配的基金产品。

筛选要点：
1. 根据用户风险偏好筛选适合的基金类型（货币基金、债券基金、混合基金、股票基金等）
2. 根据用户投资期限筛选合适的基金（短期、中期、长期）
3. 根据用户偏好行业或主题筛选相关基金
4. 考虑基金的历史业绩、波动性和风险调整收益
5. 考虑基金的费用结构和成本效益
6. 考虑基金经理的管理能力和团队稳定性

你的筛选结果应该提供多个选项，并说明每个选项的优势和适用场景。你需要使用基金搜索API获取符合条件的基金列表，然后进行进一步分析和筛选。`,
      foundationModel: bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
      knowledgeBases: [props.knowledgeBase],
    });

    // 创建Agent别名
    this.fundSelectorAgentAlias = new bedrock.AgentAlias(this, 'FundSelectorAgentAlias', {
      agent: fundSelectorAgent,
      aliasName: 'production',
    });

    // 为基金筛选Agent添加Action Group
    const searchActionGroup = new bedrock.AgentActionGroup({
      name: 'fund-search',
      description: '搜索符合条件的基金',
      executor: bedrock.ActionGroupExecutor.fromlambdaFunction(this.fundSearchFunction),
      apiSchema: bedrock.ApiSchema.fromInline(JSON.stringify({
        openapi: '3.0.0',
        info: {
          title: 'Fund Search API',
          version: '1.0.0',
          description: 'API for searching funds'
        },
        paths: {
          '/searchFunds': {
            post: {
              operationId: 'searchFunds',
              summary: '搜索基金',
              description: '根据条件搜索符合要求的基金',
              requestBody: {
                required: true,
                content: {
                  'application/json': {
                    schema: {
                      type: 'object',
                      properties: {
                        fundType: {
                          type: 'string',
                          description: '基金类型（股票型、债券型、混合型、货币型等）'
                        },
                        riskLevel: {
                          type: 'string',
                          description: '风险等级（低、中低、中、中高、高）'
                        },
                        industry: {
                          type: 'string',
                          description: '行业主题（科技、医疗、消费等）'
                        },
                        investmentHorizon: {
                          type: 'string',
                          description: '投资期限（短期、中期、长期）'
                        }
                      }
                    }
                  }
                }
              },
              responses: {
                '200': {
                  description: '成功搜索基金'
                }
              }
            }
          }
        }
      }))
    });

    // 将Action Group添加到Agent
    fundSelectorAgent.addActionGroup(searchActionGroup);
  }
}

/**
 * 基金筛选Agent构造属性
 */
export interface FundSelectorAgentProps {
  /**
   * 基金知识库
   */
  readonly knowledgeBase: bedrock.IKnowledgeBase;
}