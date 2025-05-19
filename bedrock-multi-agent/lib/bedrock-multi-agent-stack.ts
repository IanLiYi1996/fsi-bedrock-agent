import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { FinancialKnowledgeBase } from './constructs/knowledge-base';
import { ExpertAgents } from './constructs/expert-agents';
import { AnalysisAgents } from './constructs/analysis-agents';
import { PortfolioManager } from './constructs/portfolio-manager';

/**
 * AI对冲基金多Agent系统
 * 实现类似 https://github.com/virattt/ai-hedge-fund 的多Agent协作系统
 */
export class BedrockMultiAgentStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // 创建金融知识库
    const financialKnowledgeBase = new FinancialKnowledgeBase(this, 'FinancialKnowledgeBase');

    // 创建投资专家Agent
    const expertAgents = new ExpertAgents(this, 'ExpertAgents', {
      knowledgeBase: financialKnowledgeBase.knowledgeBase,
    });

    // 创建分析Agent
    const analysisAgents = new AnalysisAgents(this, 'AnalysisAgents', {
      knowledgeBase: financialKnowledgeBase.knowledgeBase,
    });

    // 创建投资组合管理Agent
    const portfolioManager = new PortfolioManager(this, 'PortfolioManager', {
      knowledgeBase: financialKnowledgeBase.knowledgeBase,
      expertAgents: {
        buffettAgentAlias: expertAgents.buffettAgentAlias,
        ackmanAgentAlias: expertAgents.ackmanAgentAlias,
        mungerAgentAlias: expertAgents.mungerAgentAlias,
      },
      analysisAgents: {
        valuationAgentAlias: analysisAgents.valuationAgentAlias,
        sentimentAgentAlias: analysisAgents.sentimentAgentAlias,
        fundamentalsAgentAlias: analysisAgents.fundamentalsAgentAlias,
        technicalsAgentAlias: analysisAgents.technicalsAgentAlias,
        riskManagerAgentAlias: analysisAgents.riskManagerAgentAlias,
      },
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

    new cdk.CfnOutput(this, 'FinancialKnowledgeBaseId', {
      value: financialKnowledgeBase.knowledgeBase.knowledgeBaseId,
      description: '金融知识库的ID',
    });

    new cdk.CfnOutput(this, 'FinancialDataBucketName', {
      value: financialKnowledgeBase.bucket.bucketName,
      description: '金融数据存储桶的名称',
    });
  }
}
