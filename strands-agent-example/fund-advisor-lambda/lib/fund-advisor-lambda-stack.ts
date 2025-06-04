import { Duration, Stack, StackProps } from "aws-cdk-lib";
import { Construct } from "constructs";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as iam from "aws-cdk-lib/aws-iam";
import * as path from "path";

/**
 * 基金顾问Lambda堆栈
 * 
 * 此堆栈定义了基金顾问Lambda函数及其权限，包括：
 * - Lambda函数
 * - Lambda层（用于依赖）
 * - IAM权限（Bedrock、DynamoDB等）
 */
export class FundAdvisorLambdaStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const packagingDirectory = path.join(__dirname, "../packaging");

    const zipDependencies = path.join(packagingDirectory, "dependencies.zip");
    const zipApp = path.join(packagingDirectory, "app.zip");

    // 创建Lambda层，包含依赖
    const dependenciesLayer = new lambda.LayerVersion(this, "DependenciesLayer", {
      code: lambda.Code.fromAsset(zipDependencies),
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_12],
      description: "基金顾问系统依赖",
    });

    // 创建Lambda函数
    const fundAdvisorFunction = new lambda.Function(this, "FundAdvisorFunction", {
      runtime: lambda.Runtime.PYTHON_3_12,
      functionName: "FundAdvisorFunction",
      description: "基金投资顾问Lambda函数",
      handler: "agent_handler.handler",
      code: lambda.Code.fromAsset(zipApp),
      timeout: Duration.seconds(60),  // 增加超时时间，因为Agent处理可能需要更长时间
      memorySize: 1024,  // 增加内存，以支持多Agent
      layers: [dependenciesLayer],
      environment: {
        KNOWLEDGE_BASE_ID: "DDBX9Y6VJ6",  // 替换为实际的知识库ID
        LOG_LEVEL: "INFO"
      }
    });

    // 添加Bedrock API调用权限
    fundAdvisorFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
        resources: ["*"],
      }),
    );

    // 添加DynamoDB访问权限
    fundAdvisorFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan",
        ],
        resources: ["*"],  // 可以限制为特定表
      }),
    );

    // 添加知识库访问权限
    fundAdvisorFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: [
          "bedrock:RetrieveAndGenerate",
          "bedrock:Retrieve",
        ],
        resources: ["*"],
      }),
    );
  }
}
