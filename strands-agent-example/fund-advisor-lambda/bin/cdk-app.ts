#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { FundAdvisorLambdaStack } from '../lib/fund-advisor-lambda-stack';

/**
 * 基金顾问Lambda CDK应用入口
 * 
 * 此文件是CDK应用的入口点，负责创建和部署基金顾问Lambda堆栈。
 * 它使用AWS CDK来定义和部署基础设施，包括Lambda函数、层和权限。
 */

const app = new cdk.App();

// 创建基金顾问Lambda堆栈
new FundAdvisorLambdaStack(app, 'FundAdvisorLambdaStack', {
  /* 如果需要，可以在此处指定堆栈属性 */
  env: { 
    account: process.env.CDK_DEFAULT_ACCOUNT, 
    region: process.env.CDK_DEFAULT_REGION || 'us-east-1'
  },
  description: '基金顾问Lambda堆栈，提供基金投资建议和分析服务'
});
