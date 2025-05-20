import { Construct } from 'constructs';
import { bedrock } from '@cdklabs/generative-ai-cdk-constructs';

/**
 * 用户画像Agent构造
 * 创建用户画像Agent，负责分析用户的风险偏好、投资目标、投资期限和流动性需求
 */
export class UserProfileAgent extends Construct {
  public readonly userProfileAgentAlias: bedrock.AgentAlias;

  constructor(scope: Construct, id: string, props: UserProfileAgentProps) {
    super(scope, id);

    // 用户画像Agent
    const userProfileAgent = new bedrock.Agent(this, 'UserProfileAgent', {
      name: 'UserProfileAgent',
      instruction: `你是用户画像分析专家，负责分析用户的风险偏好、投资目标、投资期限和流动性需求。
你需要通过用户提供的信息，建立完整的投资者画像，为基金推荐提供依据。
当分析用户时，你应该关注用户的风险承受能力、投资期限、流动性需求、投资目标和偏好行业或主题。

分析要点：
1. 用户的风险承受能力（保守型、稳健型、积极型、激进型）
2. 用户的投资期限（短期、中期、长期）
3. 用户的流动性需求（高、中、低）
4. 用户的投资目标（保值、稳健增值、积极增值）
5. 用户的偏好行业或主题（科技、医疗、消费等）
6. 用户的投资经验和知识水平
7. 用户的年龄、职业和财务状况

你的分析应该全面、客观，并根据用户的特点提供个性化的投资建议。你需要将用户信息转化为结构化的投资者画像，以便基金筛选Agent使用。`,
      foundationModel: bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
      knowledgeBases: [props.knowledgeBase],
    });

    // 创建Agent别名
    this.userProfileAgentAlias = new bedrock.AgentAlias(this, 'UserProfileAgentAlias', {
      agent: userProfileAgent,
      aliasName: 'production',
    });
  }
}

/**
 * 用户画像Agent构造属性
 */
export interface UserProfileAgentProps {
  /**
   * 基金知识库
   */
  readonly knowledgeBase: bedrock.IKnowledgeBase;
}