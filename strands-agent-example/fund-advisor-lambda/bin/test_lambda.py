#!/usr/bin/env python3
"""
Lambda函数测试脚本

此脚本用于测试Lambda函数，模拟AWS Lambda环境调用函数处理程序。
"""

import sys
import os
import json
import logging
from pathlib import Path

# 设置日志级别
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加Lambda函数代码目录到Python路径
project_root = Path(__file__).parent.parent.absolute()
lambda_dir = project_root / "lambda"
sys.path.insert(0, str(lambda_dir))

# 设置环境变量，模拟Lambda环境
os.environ["AWS_LAMBDA_FUNCTION_NAME"] = "FundAdvisorFunction"
os.environ["AWS_LAMBDA_FUNCTION_VERSION"] = "$LATEST"
os.environ["AWS_LAMBDA_FUNCTION_MEMORY_SIZE"] = "1024"
os.environ["AWS_REGION"] = "us-east-1"

# 导入Lambda处理程序
try:
    from agent_handler import handler
    logger.info("成功导入Lambda处理程序")
except ImportError as e:
    logger.error(f"导入Lambda处理程序失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

def test_lambda(query: str):
    """
    测试Lambda函数
    
    Args:
        query: 用户查询
    """
    # 创建Lambda事件对象
    event = {
        "query": query
    }
    
    # 创建Lambda上下文对象（模拟）
    class LambdaContext:
        def __init__(self):
            self.function_name = "FundAdvisorFunction"
            self.memory_limit_in_mb = 1024
            self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:FundAdvisorFunction"
            self.aws_request_id = "c6af9ac6-7b61-11e6-9a41-93e8deadbeef"
            self.log_group_name = "/aws/lambda/FundAdvisorFunction"
            self.log_stream_name = "2023/06/04/[$LATEST]c6af9ac67b6111e69a4193e8deadbeef"
            self.identity = None
            self.client_context = None
            
        def get_remaining_time_in_millis(self):
            return 60000  # 60秒
    
    context = LambdaContext()
    
    # 调用Lambda处理程序
    logger.info(f"调用Lambda处理程序，查询: {query}")
    try:
        response = handler(event, context)
        
        # 打印响应
        logger.info(f"状态码: {response.get('statusCode')}")
        logger.info("响应内容:")
        print("-" * 80)
        print(response.get('body'))
        print("-" * 80)
        
        return response
    except Exception as e:
        logger.error(f"调用Lambda处理程序时出错: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # 从命令行参数获取查询，如果没有提供，则使用默认查询
    query = sys.argv[1] if len(sys.argv) > 1 else "推荐一些低风险基金"
    
    # 测试Lambda函数
    test_lambda(query)
