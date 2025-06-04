"""
Lambda处理程序，处理基金顾问查询

此模块提供了AWS Lambda函数的处理程序，用于处理基金投资顾问查询。
它使用PortfolioManagerAgent来处理用户查询，并返回适当的响应。
"""

from agents.portfolio_manager import PortfolioManagerAgent
from utils.callback_handlers import LoggingCallbackHandler
from typing import Dict, Any
from dotenv import load_dotenv
import os


# 加载环境变量
load_dotenv()
# 如果环境变量中没有KNOWLEDGE_BASE_ID，则使用默认值
if "KNOWLEDGE_BASE_ID" not in os.environ:
    os.environ["KNOWLEDGE_BASE_ID"] = "DDBX9Y6VJ6"

def handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Lambda处理程序，处理基金顾问查询
    
    Args:
        event: Lambda事件对象，包含查询内容
        context: Lambda上下文对象
    
    Returns:
        包含响应的字典
    """
    # 创建回调处理器
    callback_handler = LoggingCallbackHandler()
    
    # 创建投资组合管理Agent
    portfolio_manager = PortfolioManagerAgent(callback_handler=callback_handler)
    
    # 获取查询内容
    query = event.get('query', '')
    if not query:
        return {
            'statusCode': 400,
            'body': '查询内容不能为空'
        }
    
    # 处理查询
    try:
        response = portfolio_manager.process_query(query)
        return {
            'statusCode': 200,
            'body': response
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'处理查询时出错: {str(e)}'
        }
