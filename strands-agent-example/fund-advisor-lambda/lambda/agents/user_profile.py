from strands import Agent, tool
from typing import Dict, Any
import sys
import os
import logging
from tools.user_info import get_user_profile, get_user_comprehensive_info
from utils.context_utils import get_current_callback_handler
from utils.agent_utils import create_agent_with_parent_callback

logger = logging.getLogger(__name__)

@tool
def user_profile_agent(query: str) -> str:
    """
    用户画像分析专家，负责分析用户的风险偏好、投资目标、投资期限和流动性需求。
    
    Args:
        query: 用户查询，通常包含用户投资偏好信息
    """
    logger.info(f"调用用户画像分析专家: {query}")
    
    # 获取当前上下文中的callback处理器
    parent_callback = get_current_callback_handler()
    
    # 使用工具函数创建带有父级callback处理器的agent
    agent = create_agent_with_parent_callback(
        Agent,
        "用户画像",
        parent_callback,
        system_prompt="""你是用户画像分析专家，负责分析用户的风险偏好、投资目标、投资期限和流动性需求。
        你需要通过用户提供的信息，建立完整的投资者画像，为基金推荐提供依据。
        当分析用户时，你应该关注用户的风险承受能力、投资期限、流动性需求、投资目标和偏好行业或主题。
        
        分析要点：
        1. 用户的风险承受能力（保守型、稳健型、积极型、激进型）
        2. 用户的投资期限（短期、中期、长期）
        3. 用户的流动性需求（高、中、低）
        4. 用户的投资目标（保值、稳健增值、积极增值）
        5. 用户的偏好行业或主题（科技、医疗、消费等）
        6. 用户的投资经验和知识水平
        7. 用户的年龄、职业和财务状况
        
        你的分析应该全面、客观，并根据用户的特点提供个性化的投资建议。你需要将用户信息转化为结构化的投资者画像，以便基金筛选Agent使用。
        
        输出格式：
        1. 风险偏好：[保守型/稳健型/积极型/激进型]
        2. 投资期限：[短期（1年以内）/中期（1-3年）/长期（3年以上）]
        3. 流动性需求：[高/中/低]
        4. 投资目标：[保值/稳健增值/积极增值]
        5. 偏好行业或主题：[具体行业或主题，如科技、医疗、消费等]
        6. 适合基金类型：[货币型/债券型/混合型/股票型/指数型]
        7. 建议资产配置：[例如：股票型基金40%，混合型基金30%，债券型基金20%，货币市场基金10%]
        8. 投资建议：[根据用户特点的具体投资建议]
        """,
        tools=[get_user_comprehensive_info, get_user_profile],
        load_tools_from_directory=False
    )
    
    # 处理查询
    response = agent(query)
    return response.message
