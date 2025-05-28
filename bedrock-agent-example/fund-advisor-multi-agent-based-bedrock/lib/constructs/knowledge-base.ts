import { Construct } from 'constructs';
import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { bedrock } from '@cdklabs/generative-ai-cdk-constructs';

/**
 * 基金知识库构造
 * 创建S3存储桶和向量知识库，用于存储和检索基金数据
 */
export class FundKnowledgeBase extends Construct {
  public readonly knowledgeBase: bedrock.VectorKnowledgeBase;
  public readonly bucket: s3.Bucket;
  public readonly dataSource: bedrock.S3DataSource;

  constructor(scope: Construct, id: string) {
    super(scope, id);

    // 创建S3存储桶，用于存储基金数据
    this.bucket = new s3.Bucket(this, 'FundDataBucket', {
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      versioned: true,
      publicReadAccess: false,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      encryption: s3.BucketEncryption.S3_MANAGED,
    });

    this.knowledgeBase = new bedrock.VectorKnowledgeBase(this, 'FinancialKnowledgeBase', {
      embeddingsModel: bedrock.BedrockFoundationModel.COHERE_EMBED_MULTILINGUAL_V3,
      instruction: '基金投资知识库，包含基金投资知识、市场数据和投资策略信息。',
    });

    // 创建S3数据源
    this.dataSource = new bedrock.S3DataSource(this, 'DataSource', {
      bucket: this.bucket,
      knowledgeBase: this.knowledgeBase,
      dataSourceName: 'financial-data',
      chunkingStrategy: bedrock.ChunkingStrategy.fixedSize({
        maxTokens: 500,
        overlapPercentage: 20
      }),
    });
  }
}