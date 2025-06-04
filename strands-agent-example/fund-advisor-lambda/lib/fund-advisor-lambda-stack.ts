import { Duration, Stack, StackProps } from "aws-cdk-lib";
import { Construct } from "constructs";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as iam from "aws-cdk-lib/aws-iam";
import * as path from "path";

/**
 * 基金顾问Lambda堆栈
 * 
 * 此堆栈定义了基金顾问Lambda函数及其权限，包括：
 * - Lambda函数（使用Docker容器镜像）
 * - IAM权限（Bedrock、DynamoDB等）
 */
export class FundAdvisorLambdaStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // 创建Lambda函数（使用Docker容器镜像）
    const fundAdvisorFunction = new lambda.DockerImageFunction(this, "FundAdvisorFunction", {
      functionName: "FundAdvisorFunction",
      description: "基金投资顾问Lambda函数",
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '..')),
      timeout: Duration.seconds(60),  // 增加超时时间，因为Agent处理可能需要更长时间
      memorySize: 1024,  // 增加内存，以支持多Agent
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
