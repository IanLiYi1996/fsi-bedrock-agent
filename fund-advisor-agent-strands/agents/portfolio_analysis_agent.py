from strands import Agent, tool
from typing import Dict, Any
import sys
import os
import logging

# 添加项目根目录到Python路径，以便导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.holdings_performance_analyst import holdings_performance_analyst

logger = logging.getLogger(__name__)

@tool
def portfolio_analysis_agent(query: str) -> str:
    """
    用户组合分析专家，负责分析用户持仓基金的投资价值和风险，给出持有或调仓建议。
    
    Args:
        query: 用户查询，通常包含用户ID
    """
    logger.info(f"调用用户组合分析专家: {query}")
    
    # 创建分析Agent
    agent = Agent(
        system_prompt="""你是用户组合分析专家，负责分析用户持仓基金的投资价值和风险，给出持有或调仓建议。
        你需要评估用户的整体投资组合，分析各基金的表现、风险和相互关系，并根据用户的风险偏好和投资期限给出持有或调仓建议。
        当分析用户组合时，你应该关注组合的整体收益、风险分散度、资产配置合理性和各基金的表现。
        
        分析要点：
        1. 用户风险偏好和投资期限
        2. 用户持仓基金的基本信息和表现
        3. 组合的整体收益和风险水平
        4. 组合的资产配置和行业分布
        5. 各基金之间的相关性和分散化效果
        6. 各基金的真实盈利可能性和持仓表现
        7. 基于用户特点和市场环境的持有或调仓建议
        
        你的分析应该客观、全面，并提供具体的数据支持。你需要综合考虑用户的风险偏好、投资期限和持仓基金的表现，给出持有或调仓的建议。
        
        输出格式：
        1. 用户投资画像：[风险偏好、投资期限]
        2. 持仓组合概览：
           - 基金数量：[持仓基金数量]
           - 总投资金额：[总投资金额]
           - 资产配置：[股票型/混合型/债券型/货币型占比]
        3. 各基金分析：
           - 基金名称：[基金名称]
           - 投资金额：[投资金额]
           - 占比：[占总投资的比例]
           - 表现评估：[表现良好/一般/不佳]
           - 风险评估：[风险高/中/低]
           - 持有建议：[继续持有/增持/减持/调仓]
        4. 组合整体评估：[组合的整体收益和风险评估]
        5. 调仓建议：
           - 建议减持：[建议减持的基金及理由]
           - 建议增持：[建议增持的基金及理由]
           - 建议新增：[建议新增的基金类型或具体基金]
        6. 总结建议：[对用户投资组合的总体建议和优化方向]
        """,
        tools=[holdings_performance_analyst]
    )
    
    # 处理查询
    response = agent(query)
    return response.message