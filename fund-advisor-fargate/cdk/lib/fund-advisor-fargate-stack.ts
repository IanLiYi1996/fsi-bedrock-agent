import { Stack, StackProps, Duration, RemovalPolicy, CfnOutput } from "aws-cdk-lib";
import { Construct } from "constructs";
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as ecs from "aws-cdk-lib/aws-ecs";
import * as iam from "aws-cdk-lib/aws-iam";
import * as logs from "aws-cdk-lib/aws-logs";
import * as elbv2 from "aws-cdk-lib/aws-elasticloadbalancingv2";
import * as ecrAssets from "aws-cdk-lib/aws-ecr-assets";
import * as path from "path";

export class FundAdvisorFargateStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // 创建VPC
    const vpc = new ec2.Vpc(this, "FundAdvisorVpc", {
      maxAzs: 2,
      natGateways: 1,
    });

    // 创建ECS集群
    const cluster = new ecs.Cluster(this, "FundAdvisorCluster", {
      vpc,
    });

    // 创建日志组
    const logGroup = new logs.LogGroup(this, "FundAdvisorServiceLogs", {
      retention: logs.RetentionDays.ONE_WEEK,
      removalPolicy: RemovalPolicy.DESTROY,
    });

    // 创建任务执行角色
    const executionRole = new iam.Role(this, "FundAdvisorTaskExecutionRole", {
      assumedBy: new iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
      managedPolicies: [iam.ManagedPolicy.fromAwsManagedPolicyName("service-role/AmazonECSTaskExecutionRolePolicy")],
    });

    // 创建任务角色
    const taskRole = new iam.Role(this, "FundAdvisorTaskRole", {
      assumedBy: new iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
    });

    // 添加Bedrock API调用权限
    taskRole.addToPolicy(
      new iam.PolicyStatement({
        actions: ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
        resources: ["*"],
      }),
    );

    // 添加DynamoDB访问权限
    taskRole.addToPolicy(
      new iam.PolicyStatement({
        actions: [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan",
        ],
        resources: ["*"], // 可以限制为特定表
      }),
    );

    // 添加知识库访问权限
    taskRole.addToPolicy(
      new iam.PolicyStatement({
        actions: [
          "bedrock:RetrieveAndGenerate",
          "bedrock:Retrieve",
        ],
        resources: ["*"],
      }),
    );

    // 创建任务定义
    const taskDefinition = new ecs.FargateTaskDefinition(this, "FundAdvisorTaskDefinition", {
      memoryLimitMiB: 2048, // 增加内存以支持多Agent
      cpu: 1024, // 增加CPU以支持多Agent
      executionRole,
      taskRole,
    });

    // 使用Docker目录中的Dockerfile
    const dockerAsset = new ecrAssets.DockerImageAsset(this, "FundAdvisorImage", {
      directory: path.join(__dirname, "../../docker"),
      file: "Dockerfile",
    });

    // 添加容器到任务定义
    taskDefinition.addContainer("FundAdvisorContainer", {
      image: ecs.ContainerImage.fromDockerImageAsset(dockerAsset),
      logging: ecs.LogDrivers.awsLogs({
        streamPrefix: "fund-advisor-service",
        logGroup,
      }),
      environment: {
        // 添加环境变量
        LOG_LEVEL: "INFO",
        KNOWLEDGE_BASE_ID: "DDBX9Y6VJ6", // 替换为实际的知识库ID
      },
      portMappings: [
        {
          containerPort: 8000,
          protocol: ecs.Protocol.TCP,
        },
      ],
    });

    // 创建Fargate服务
    const service = new ecs.FargateService(this, "FundAdvisorService", {
      cluster,
      taskDefinition,
      desiredCount: 2, // 运行2个实例以实现高可用
      assignPublicIp: false,
      vpcSubnets: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
      circuitBreaker: {
        rollback: true,
      },
      securityGroups: [
        new ec2.SecurityGroup(this, "FundAdvisorServiceSG", {
          vpc,
          description: "Security group for Fund Advisor Fargate Service",
          allowAllOutbound: true,
        }),
      ],
      minHealthyPercent: 100,
      maxHealthyPercent: 200,
      healthCheckGracePeriod: Duration.seconds(60),
    });

    // 创建应用负载均衡器
    const lb = new elbv2.ApplicationLoadBalancer(this, "FundAdvisorLB", {
      vpc,
      internetFacing: true,
    });

    // 创建监听器
    const listener = lb.addListener("FundAdvisorListener", {
      port: 80,
    });

    // 添加目标组到监听器
    listener.addTargets("FundAdvisorTargets", {
      port: 8000,
      targets: [service],
      healthCheck: {
        path: "/health",
        interval: Duration.seconds(30),
        timeout: Duration.seconds(5),
        healthyHttpCodes: "200",
      },
      deregistrationDelay: Duration.seconds(30),
    });

    // 输出负载均衡器DNS名称
    new CfnOutput(this, "FundAdvisorServiceEndpoint", {
      value: lb.loadBalancerDnsName,
      description: "The DNS name of the load balancer for the Fund Advisor Service",
      exportName: "FundAdvisorServiceEndpoint",
    });
  }
}