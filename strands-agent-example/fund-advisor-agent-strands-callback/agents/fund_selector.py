from strands import Agent, tool
from typing import Dict, Any
import sys
import os
import logging

# 添加项目根目录到Python路径，以便导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)
from tools.fund_info import get_fund_by_code, get_fund_search_results, get_fund_fees_by_code, get_fund_manager_by_code, get_fund_performance_by_code

@tool
def fund_selector_agent(query: str) -> str:
    """
    基金筛选专家，负责根据用户偏好和投资目标筛选合适的基金。
    
    Args:
        query: 用户查询，通常包含用户画像信息
    """
    logger.info(f"调用基金筛选专家: {query}")
    
    # 创建基金筛选Agent
    agent = Agent(
        system_prompt="""你是基金筛选专家，负责根据用户偏好和投资目标筛选合适的基金。
        你需要考虑基金类型、风险等级、历史业绩和费用结构等多维度因素。
        当筛选基金时，你应该根据用户的风险偏好、投资期限和投资目标，找到最匹配的基金产品。
        
        筛选要点：
        1. 根据用户风险偏好筛选适合的基金类型（货币基金、债券基金、混合基金、股票基金等）
        2. 根据用户投资期限筛选合适的基金（短期、中期、长期）
        3. 根据用户偏好行业或主题筛选相关基金
        4. 考虑基金的历史业绩、波动性和风险调整收益
        5. 考虑基金的费用结构和成本效益
        6. 考虑基金经理的管理能力和团队稳定性
        
        你的筛选结果应该提供多个选项，并说明每个选项的优势和适用场景。你需要使用基金搜索工具获取符合条件的基金列表，然后进行进一步分析和筛选。
        
        输出格式：
        1. 筛选条件：[根据用户画像提取的筛选条件]
        2. 推荐基金列表：
           - 基金代码：[基金代码]
           - 基金名称：[基金名称]
           - 基金类型：[基金类型]
           - 风险等级：[风险等级]
           - 推荐理由：[为什么推荐这只基金]
        3. 投资建议：[如何配置这些基金，以及其他投资建议]
        """,
        tools=[get_fund_by_code, get_fund_search_results, get_fund_fees_by_code, get_fund_manager_by_code, get_fund_performance_by_code],
        load_tools_from_directory=False
    )
    
    # 处理查询
    response = agent(query)
    return response.message
