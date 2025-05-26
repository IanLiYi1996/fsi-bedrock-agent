from strands import Agent, tool
from typing import Dict, Any
import sys
import os
import logging

# 添加项目根目录到Python路径，以便导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.fund_data import get_fund_info, get_fund_holdings, get_stock_news, get_stock_performance

logger = logging.getLogger(__name__)

@tool
def holdings_performance_analyst(query: str) -> str:
    """
    基金持仓表现分析专家，负责分析基金持仓股票的表现和相关资讯，判断基金真实盈利可能性和表现是否与持仓信息相符。
    
    Args:
        query: 用户查询，通常包含基金代码
    """
    logger.info(f"调用基金持仓表现分析专家: {query}")
    
    # 创建分析Agent
    agent = Agent(
        system_prompt="""你是基金持仓表现分析专家，负责分析基金持仓股票的表现和相关资讯，判断基金真实盈利可能性和表现是否与持仓信息相符。
        你需要评估基金重仓股的业绩表现、行业前景和相关新闻资讯，判断基金的真实盈利可能性。
        当分析基金时，你应该关注重仓股的股价表现、财务指标、分析师评级和相关新闻资讯。
        
        分析要点：
        1. 基金重仓股的近期表现（股价涨跌、市场表现）
        2. 重仓股的财务指标（PE、PB、收入增长、利润增长）
        3. 重仓股的分析师评级和行业排名
        4. 重仓股的相关新闻资讯和市场情绪
        5. 基金业绩与重仓股表现的一致性分析
        6. 基金持仓结构的合理性和风险评估
        7. 基于持仓分析的基金真实盈利可能性判断
        8. 持有建议（适合持有、谨慎持有、建议减持）
        
        你的分析应该客观、全面，并提供具体的数据支持。你需要综合考虑基金持仓股票的表现和相关资讯，判断基金真实盈利的可能性以及基金的表现是否与持仓信息相符，最终给出是否适合持有的建议。
        
        输出格式：
        1. 基金基本信息：[基金代码、名称、类型等]
        2. 重仓股表现分析：
           - 股票名称：[股票名称]
           - 近期表现：[股价涨跌、市场表现]
           - 财务指标：[PE、PB、收入增长、利润增长]
           - 分析师评级：[买入/持有/卖出评级]
           - 相关新闻：[重要新闻摘要及情绪分析]
        3. 持仓与业绩一致性分析：[基金业绩与重仓股表现的一致性分析]
        4. 真实盈利可能性评估：[基于持仓分析的基金真实盈利可能性判断]
        5. 持有建议：[适合持有/谨慎持有/建议减持]
        6. 建议理由：[给出持有建议的具体理由]
        """,
        tools=[get_fund_info, get_fund_holdings, get_stock_news, get_stock_performance]
    )
    
    # 处理查询
    response = agent(query)
    return response.message