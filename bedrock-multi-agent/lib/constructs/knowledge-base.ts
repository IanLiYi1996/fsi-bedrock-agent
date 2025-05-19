import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { bedrock } from '@cdklabs/generative-ai-cdk-constructs';

/**
 * 金融知识库构造
 * 创建S3存储桶和向量知识库，用于存储和检索金融数据
 */
export class FinancialKnowledgeBase extends Construct {
  public readonly knowledgeBase: bedrock.VectorKnowledgeBase;
  public readonly bucket: s3.Bucket;
  public readonly dataSource: bedrock.S3DataSource;

  constructor(scope: Construct, id: string) {
    super(scope, id);

    // 创建S3存储桶用于金融数据和知识库
    this.bucket = new s3.Bucket(this, 'FinancialDataBucket', {
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      versioned: true,
      publicReadAccess: false,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      encryption: s3.BucketEncryption.S3_MANAGED,
    });

    // 创建金融知识库
    this.knowledgeBase = new bedrock.VectorKnowledgeBase(this, 'FinancialKnowledgeBase', {
      embeddingsModel: bedrock.BedrockFoundationModel.TITAN_EMBED_TEXT_V1,
      instruction: '使用此知识库回答有关金融市场、公司财务数据和投资策略的问题。',
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