from strands import Agent, tool
from typing import Dict, Any
import sys
import os
import logging

# 添加项目根目录到Python路径，以便导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)
from tools.fund_info import get_fund_by_code, get_fund_performance_by_code, get_fund_individual_analysis_by_code
from utils.context_utils import get_current_callback_handler
from utils.agent_utils import create_agent_with_parent_callback

@tool
def strategy_performance_expert(query: str) -> str:
    """
    基金策略与业绩专家，负责分析基金的投资策略、风格以及历史业绩、波动性和风险调整收益。
    
    Args:
        query: 用户查询，通常包含基金代码
    """
    logger.info(f"调用基金策略与业绩专家: {query}")
    
    # 获取当前上下文中的callback处理器
    parent_callback = get_current_callback_handler()
    
    # 使用工具函数创建带有父级callback处理器的agent
    agent = create_agent_with_parent_callback(
        Agent,
        "策略专家",
        parent_callback,
        system_prompt="""你是基金策略与业绩专家，负责分析基金的投资策略、风格以及历史业绩、波动性和风险调整收益。
        你需要评估基金的投资理念、策略执行一致性、适应市场变化的能力，以及在不同时间段的表现、与基准的对比以及风险调整后的收益指标。
        
        当分析基金时，你应该关注以下方面：
        
        策略分析：
        1. 基金的投资策略是否清晰明确
        2. 基金经理是否严格执行既定策略
        3. 策略在不同市场环境下的适应性
        4. 投资风格的一致性和漂移情况
        5. 选股策略的有效性和独特性
        
        业绩分析：
        1. 基金在不同时间段（1月、3月、6月、1年、3年、5年）的收益表现
        2. 基金与业绩比较基准的对比
        3. 基金的波动性指标（标准差、最大回撤）
        4. 风险调整收益指标（夏普比率、信息比率、特雷诺比率）
        5. 基金在不同市场环境下的表现一致性
        
        你的分析应该客观、专业，并提供具体的数据支持。你需要综合评估基金的策略和业绩，判断基金的投资价值和风险。
        
        输出格式：
        1. 基金基本信息：[基金代码、名称、类型等]
        2. 投资策略分析：
           - 投资策略概述
           - 策略执行一致性评估
           - 投资风格分析
           - 选股策略评估
           - 策略适应性分析
        3. 业绩表现分析：
           - 不同时间段收益表现
           - 与基准对比分析
           - 波动性指标分析
           - 风险调整收益分析
           - 不同市场环境下的表现
        4. 综合评估：[基于策略和业绩的综合评估]
        5. 投资建议：[适合投资/谨慎投资/不建议投资]
        6. 建议理由：[给出投资建议的具体理由]
        """,
        tools=[get_fund_by_code, get_fund_performance_by_code, get_fund_individual_analysis_by_code],
        load_tools_from_directory=False
    )
    
    # 处理查询
    response = agent(query)
    return response.message
