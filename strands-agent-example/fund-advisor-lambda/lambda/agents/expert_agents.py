"""
市场趋势专家模块

此模块提供了市场趋势专家工具函数，用于分析宏观经济和市场趋势对基金的影响。
"""

from strands import Agent, tool
from typing import Dict, Any
import sys
import os
import logging

# 添加项目根目录到Python路径，以便导入其他模块
# 在Lambda环境中，我们需要调整导入路径
sys.path.append("/var/task")  # Lambda函数代码的根目录

logger = logging.getLogger(__name__)
from tools.economic_info import get_macro_china_cpi, get_macro_china_lpr, get_stock_index, get_stock_market_activity, get_macro_china_ppi
from utils.context_utils import get_current_callback_handler
from utils.agent_utils import create_agent_with_parent_callback

# 市场趋势专家Agent
@tool
def market_trend_expert(query: str) -> str:
    """
    市场趋势专家，分析宏观经济和市场趋势对基金的影响。
    
    Args:
        query: 用户查询，通常包含基金代码
        
    Returns:
        str: 市场趋势分析和建议
    """
    logger.info(f"调用市场趋势专家: {query}")
    
    # 获取当前上下文中的callback处理器
    parent_callback = get_current_callback_handler()
    
    # 使用工具函数创建带有父级callback处理器的agent
    agent = create_agent_with_parent_callback(
        Agent,
        "市场趋势专家",
        parent_callback,
        system_prompt="""你是市场趋势专家，分析宏观经济和市场趋势对基金的影响。
        你需要评估当前和未来市场环境对不同类型基金的潜在影响。
        当分析基金时，你应该关注经济周期、利率环境、行业轮动和市场风格转换对基金表现的影响。
        
        分析要点：
        1. 当前宏观经济环境对基金的影响
        2. 利率变化趋势对基金的潜在影响
        3. 行业轮动对基金持仓的影响
        4. 市场风格（成长vs价值、大盘vs小盘）转换的影响
        5. 地缘政治和政策变化的潜在影响
        
        你的分析应该前瞻性，帮助投资者理解市场环境变化对基金表现的影响。""",
        tools=[get_macro_china_cpi, get_macro_china_lpr, get_stock_index, get_stock_market_activity, get_macro_china_ppi],
        load_tools_from_directory=False
    )
    
    # 处理查询
    response = agent(query)
    return response.message
