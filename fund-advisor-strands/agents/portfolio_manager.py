from strands import Agent, tool
from typing import Dict, Any, Optional
import sys
import os
import logging

# 添加项目根目录到Python路径，以便导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.fund_data import get_fund_info
from agents.expert_agents import fund_strategy_expert, asset_allocation_expert, market_trend_expert
from agents.analysis_agents import performance_analyst, holdings_analyst, manager_analyst, fees_analyst
from agents.user_profile import user_profile_agent
from agents.fund_selector import fund_selector_agent

logger = logging.getLogger(__name__)

class PortfolioManagerAgent:
    def __init__(self):
        """初始化投资组合管理Agent"""
        logger.info("初始化投资组合管理Agent")
        
        # 创建投资组合管理Agent
        self.agent = Agent(
            system_prompt="""你是投资组合管理Agent，负责整合各专家意见和分析结果，并为用户提供基金投资建议。
            你有两个主要职责：
            1. 分析用户提供的基金，评估其投资价值和风险，提供持仓建议
            2. 根据用户的投资偏好，推荐合适的基金产品
            
            当用户提供基金代码或名称时，你应该分析该基金并提供全面的投资建议。
            当用户提供投资偏好时，你应该推荐符合其需求的基金产品。
            
            你的建议应该考虑用户的投资目标、风险承受能力和市场环境。你需要整合各个专家Agent和分析Agent的意见，形成全面、客观的投资建议。
            
            分析基金时，你应该：
            1. 获取基金基本信息
            2. 调用各个分析Agent进行专项分析
            3. 调用各个专家Agent获取专业意见
            4. 整合所有分析结果，形成综合评估
            
            推荐基金时，你应该：
            1. 调用用户画像Agent分析用户需求
            2. 调用基金筛选Agent获取符合条件的基金
            3. 整合专家意见，形成最终推荐
            
            你的回答应该专业、全面，并提供具体的数据支持。避免使用过于技术性的术语，确保普通投资者也能理解你的建议。""",
            tools=[
                # 专家Agent
                fund_strategy_expert,
                asset_allocation_expert,
                market_trend_expert,
                # 分析Agent
                performance_analyst,
                holdings_analyst,
                manager_analyst,
                fees_analyst,
                # 用户画像和基金筛选Agent
                user_profile_agent,
                fund_selector_agent,
                # 基金数据工具
                get_fund_info
            ]
        )
    
    @tool
    def analyze_fund(self, fund_code: str) -> str:
        """
        分析指定基金，整合各专家意见
        
        Args:
            fund_code: 基金代码
        """
        logger.info(f"分析基金: {fund_code}")
        
        # 构建分析查询
        query = f"分析基金 {fund_code} 的投资价值和风险"
        
        # 调用投资组合管理Agent
        response = self.agent(query)
        return response.message
    
    @tool
    def recommend_funds(self, risk_preference: str, investment_horizon: str, preferred_industry: Optional[str] = None) -> str:
        """
        根据用户偏好推荐基金
        
        Args:
            risk_preference: 风险偏好
            investment_horizon: 投资期限
            preferred_industry: 偏好行业
        """
        logger.info(f"推荐基金: 风险偏好={risk_preference}, 投资期限={investment_horizon}, 偏好行业={preferred_industry}")
        
        # 构建推荐查询
        query = f"我是一个风险偏好{risk_preference}、投资期限{investment_horizon}"
        if preferred_industry:
            query += f"、偏好{preferred_industry}行业"
        query += "的投资者，请推荐适合我的基金"
        
        # 调用投资组合管理Agent
        response = self.agent(query)
        return response.message
    
    def process_query(self, query: str) -> str:
        """
        处理用户查询
        
        Args:
            query: 用户查询
        """
        logger.info(f"处理用户查询: {query}")
        
        # 调用投资组合管理Agent
        response = self.agent(query)
        return response.message
