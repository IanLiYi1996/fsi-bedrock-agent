#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { FundAdvisorFargateStack } from '../lib/fund-advisor-fargate-stack';

const app = new cdk.App();
new FundAdvisorFargateStack(app, 'FundAdvisorFargateStack', {
  /* 如果需要，可以在这里指定堆栈属性 */
  env: { 
    account: process.env.CDK_DEFAULT_ACCOUNT, 
    region: process.env.CDK_DEFAULT_REGION || 'ap-northeast-1' 
  },
  description: '基金投顾多Agent系统的Fargate部署'
});

app.synth();