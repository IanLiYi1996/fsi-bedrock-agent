from strands import Agent, tool
from typing import Dict, Any, AsyncGenerator
import sys
import os
import logging

# 添加项目根目录到Python路径，以便导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)
from tools.stock_info import get_stock_info_by_code, get_stock_news_by_code, get_stock_performance_by_code
from tools.fund_info import get_fund_by_code, get_fund_holdings_by_code, get_fund_performance_by_code

@tool
def comprehensive_holdings_analyst(query: str) -> str:
    """
    综合持仓分析专家，负责分析基金的持仓结构、行业分布、重仓股以及持仓股票的表现和相关资讯，
    判断基金真实盈利可能性和表现是否与持仓信息相符。
    
    Args:
        query: 用户查询，通常包含基金代码
    """
    logger.info(f"调用综合持仓分析专家: {query}")
    
    # 创建分析Agent
    agent = Agent(
        system_prompt="""你是综合持仓分析专家，负责分析基金的持仓结构、行业分布、重仓股以及持仓股票的表现和相关资讯，
        判断基金真实盈利可能性和表现是否与持仓信息相符。
        
        你需要评估基金的持仓集中度、行业配置、个股选择以及重仓股的业绩表现、行业前景和相关新闻资讯。
        当分析基金时，你应该关注以下方面：
        
        持仓结构分析：
        1. 基金的前十大重仓股及其占比
        2. 基金的行业配置分布及其与基准的偏离度
        3. 基金持仓的集中度和分散度
        4. 重仓股的质量和潜在风险
        5. 持仓变动趋势及其反映的投资策略变化
        
        持仓表现分析：
        1. 重仓股的近期表现（股价涨跌、市场表现）
        2. 重仓股的财务指标（PE、PB、收入增长、利润增长）
        3. 重仓股的分析师评级和行业排名
        4. 重仓股的相关新闻资讯和市场情绪
        5. 基金业绩与重仓股表现的一致性分析
        6. 基于持仓分析的基金真实盈利可能性判断
        7. 持有建议（适合持有、谨慎持有、建议减持）
        
        你的分析应该深入、专业，帮助投资者理解基金的实际投资方向和风格，并判断基金真实盈利的可能性以及基金的表现是否与持仓信息相符。
        
        输出格式：
        1. 基金基本信息：[基金代码、名称、类型等]
        2. 持仓结构分析：
           - 前十大重仓股及占比
           - 行业配置分布
           - 持仓集中度评估
           - 持仓变动趋势分析
        3. 重仓股表现分析：
           - 股票名称：[股票名称]
           - 近期表现：[股价涨跌、市场表现]
           - 财务指标：[PE、PB、收入增长、利润增长]
           - 分析师评级：[买入/持有/卖出评级]
           - 相关新闻：[重要新闻摘要及情绪分析]
        4. 持仓与业绩一致性分析：[基金业绩与重仓股表现的一致性分析]
        5. 真实盈利可能性评估：[基于持仓分析的基金真实盈利可能性判断]
        6. 持有建议：[适合持有/谨慎持有/建议减持]
        7. 建议理由：[给出持有建议的具体理由]
        """,
        tools=[get_fund_by_code, get_fund_holdings_by_code, get_fund_performance_by_code, get_stock_info_by_code, get_stock_news_by_code, get_stock_performance_by_code],
        load_tools_from_directory=False
    )
    
    # 处理查询
    response = agent(query)
    return response.message

@tool
async def comprehensive_holdings_analyst_stream(query: str) -> AsyncGenerator[Dict[str, Any], None]:
    """
    流式版本的综合持仓分析专家，负责分析基金的持仓结构、行业分布、重仓股以及持仓股票的表现和相关资讯，
    判断基金真实盈利可能性和表现是否与持仓信息相符。
    
    Args:
        query: 用户查询，通常包含基金代码
    
    Returns:
        AsyncGenerator: 异步生成器，生成流式响应事件
    """
    logger.info(f"调用流式综合持仓分析专家: {query}")
    
    # 创建分析Agent
    agent = Agent(
        system_prompt="""你是综合持仓分析专家，负责分析基金的持仓结构、行业分布、重仓股以及持仓股票的表现和相关资讯，
        判断基金真实盈利可能性和表现是否与持仓信息相符。
        
        你需要评估基金的持仓集中度、行业配置、个股选择以及重仓股的业绩表现、行业前景和相关新闻资讯。
        当分析基金时，你应该关注以下方面：
        
        持仓结构分析：
        1. 基金的前十大重仓股及其占比
        2. 基金的行业配置分布及其与基准的偏离度
        3. 基金持仓的集中度和分散度
        4. 重仓股的质量和潜在风险
        5. 持仓变动趋势及其反映的投资策略变化
        
        持仓表现分析：
        1. 重仓股的近期表现（股价涨跌、市场表现）
        2. 重仓股的财务指标（PE、PB、收入增长、利润增长）
        3. 重仓股的分析师评级和行业排名
        4. 重仓股的相关新闻资讯和市场情绪
        5. 基金业绩与重仓股表现的一致性分析
        6. 基于持仓分析的基金真实盈利可能性判断
        7. 持有建议（适合持有、谨慎持有、建议减持）
        
        你的分析应该深入、专业，帮助投资者理解基金的实际投资方向和风格，并判断基金真实盈利的可能性以及基金的表现是否与持仓信息相符。
        
        输出格式：
        1. 基金基本信息：[基金代码、名称、类型等]
        2. 持仓结构分析：
           - 前十大重仓股及占比
           - 行业配置分布
           - 持仓集中度评估
           - 持仓变动趋势分析
        3. 重仓股表现分析：
           - 股票名称：[股票名称]
           - 近期表现：[股价涨跌、市场表现]
           - 财务指标：[PE、PB、收入增长、利润增长]
           - 分析师评级：[买入/持有/卖出评级]
           - 相关新闻：[重要新闻摘要及情绪分析]
        4. 持仓与业绩一致性分析：[基金业绩与重仓股表现的一致性分析]
        5. 真实盈利可能性评估：[基于持仓分析的基金真实盈利可能性判断]
        6. 持有建议：[适合持有/谨慎持有/建议减持]
        7. 建议理由：[给出持有建议的具体理由]
        """,
        tools=[get_fund_by_code, get_fund_holdings_by_code, get_fund_performance_by_code, get_stock_info_by_code, get_stock_news_by_code, get_stock_performance_by_code],
        load_tools_from_directory=False,
        callback_handler=None  # 禁用默认回调以避免重复输出
    )
    
    # 使用stream_async方法获取异步迭代器
    agent_stream = agent.stream_async(query)
    
    # 返回异步迭代器
    async for event in agent_stream:
        yield event
