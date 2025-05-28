import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { FundKnowledgeBase } from '../../fund-advisor-multi-agent/lib/constructs/knowledge-base';
import { ExpertAgents } from '../../fund-advisor-multi-agent/lib/constructs/expert-agents';
import { AnalysisAgents } from '../../fund-advisor-multi-agent/lib/constructs/analysis-agents';
import { UserProfileAgent } from '../../fund-advisor-multi-agent/lib/constructs/user-profile-agent';
import { FundSelectorAgent } from '../../fund-advisor-multi-agent/lib/constructs/fund-selector-agent';
import { PortfolioManager } from '../../fund-advisor-multi-agent/lib/constructs/portfolio-manager';
// import * as sqs from 'aws-cdk-lib/aws-sqs';

export class FundAdvisorMultiAgentStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // 创建基金知识库
    const fundKnowledgeBase = new FundKnowledgeBase(this, 'FundKnowledgeBase');

    // 创建专家Agent
    const expertAgents = new ExpertAgents(this, 'ExpertAgents', {
      knowledgeBase: fundKnowledgeBase.knowledgeBase,
    });

    // 创建分析Agent
    const analysisAgents = new AnalysisAgents(this, 'AnalysisAgents', {
      knowledgeBase: fundKnowledgeBase.knowledgeBase,
    });

    // 创建用户画像Agent
    const userProfileAgent = new UserProfileAgent(this, 'UserProfileAgent', {
      knowledgeBase: fundKnowledgeBase.knowledgeBase,
    });

    // 创建基金筛选Agent
    const fundSelectorAgent = new FundSelectorAgent(this, 'FundSelectorAgent', {
      knowledgeBase: fundKnowledgeBase.knowledgeBase,
    });

    // 创建投资组合管理Agent
    const portfolioManager = new PortfolioManager(this, 'PortfolioManager', {
      knowledgeBase: fundKnowledgeBase.knowledgeBase,
      expertAgents: {
        fundStrategyAgentAlias: expertAgents.fundStrategyAgentAlias,
        assetAllocationAgentAlias: expertAgents.assetAllocationAgentAlias,
        marketTrendAgentAlias: expertAgents.marketTrendAgentAlias,
      },
      analysisAgents: {
        performanceAgentAlias: analysisAgents.performanceAgentAlias,
        holdingsAgentAlias: analysisAgents.holdingsAgentAlias,
        managerAgentAlias: analysisAgents.managerAgentAlias,
        feesAgentAlias: analysisAgents.feesAgentAlias,
      },
      userProfileAgentAlias: userProfileAgent.userProfileAgentAlias,
      fundSelectorAgentAlias: fundSelectorAgent.fundSelectorAgentAlias,
    });

    // 输出重要资源的ARN
    new cdk.CfnOutput(this, 'PortfolioManagerAgentId', {
      value: portfolioManager.portfolioManagerAgent.agentId,
      description: '投资组合管理Agent的ID',
    });

    new cdk.CfnOutput(this, 'PortfolioManagerAgentAliasId', {
      value: portfolioManager.portfolioManagerAgentAlias.aliasId || '',
      description: '投资组合管理Agent别名的ID',
    });

    new cdk.CfnOutput(this, 'FundKnowledgeBaseId', {
      value: fundKnowledgeBase.knowledgeBase.knowledgeBaseId,
      description: '基金知识库的ID',
    });

    new cdk.CfnOutput(this, 'FundDataBucketName', {
      value: fundKnowledgeBase.bucket.bucketName,
      description: '基金数据存储桶的名称',
    });
  }
}
