import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as path from 'path';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import { bedrock } from '@cdklabs/generative-ai-cdk-constructs';

export class BedrockAgentStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // 创建一个基本的Bedrock Agent
    const agent = new bedrock.Agent(this, 'LiteratureAgent', {
      foundationModel: bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
      instruction: 'You are a helpful and friendly agent that answers questions about literature.',
      userInputEnabled: true,
      shouldPrepareAgent: true,
    });

    // 创建一个Python Lambda函数作为Action Group的执行器
    const actionGroupFunction = new lambda.Function(this, 'ActionGroupFunction', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'app.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../lambda/action-group-python')),
    });

    // 创建一个Action Group
    const actionGroup = new bedrock.AgentActionGroup({
      name: 'query-library',
      description: 'Use these functions to get information about the books in the library.',
      executor: bedrock.ActionGroupExecutor.fromlambdaFunction(actionGroupFunction),
      enabled: true,
      apiSchema: bedrock.ApiSchema.fromLocalAsset(path.join(__dirname, 'action-group.yaml')),
    });

    // 将Action Group添加到Agent
    agent.addActionGroup(actionGroup);

    // 创建Agent别名
    const agentAlias = new bedrock.AgentAlias(this, 'ProductionAlias', {
      agent: agent,
      aliasName: 'production',
      description: 'Production version of the Literature Agent',
    });

    // 输出Agent和Agent别名的ARN
    new cdk.CfnOutput(this, 'AgentArn', {
      value: agent.agentArn,
      description: 'The ARN of the Bedrock Agent',
    });

    // 输出Agent别名ID，而不是ARN
    new cdk.CfnOutput(this, 'AgentAliasId', {
      value: agentAlias.aliasId || agentAlias.aliasName,
      description: 'The ID of the Bedrock Agent Alias',
    });
  }
}
