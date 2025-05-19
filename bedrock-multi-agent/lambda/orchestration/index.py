import json
import logging
import boto3
import os

# 配置日志
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 初始化Bedrock客户端
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')

def handler(event, context):
    """
    自定义编排Lambda函数
    """
    logger.info(f"收到的事件: {json.dumps(event)}")
    
    try:
        # 解析用户输入
        input_text = event.get('inputText', '')
        session_id = event.get('sessionId', '')
        agent_id = event.get('agentId', '')
        agent_alias_id = event.get('agentAliasId', '')
        
        # 提取股票代码
        ticker = extract_ticker(input_text)
        if not ticker:
            return {
                "completion": "请提供有效的股票代码，例如 'AAPL'、'MSFT' 或 'GOOGL'。"
            }
        
        # 1. 调用投资专家Agent获取分析
        expert_responses = []
        expert_agents = {
            'WarrenBuffettAgent': os.environ.get('WARREN_BUFFETT_AGENT_ALIAS_ID', ''),
            'BillAckmanAgent': os.environ.get('BILL_ACKMAN_AGENT_ALIAS_ID', ''),
            'CharlieMongerAgent': os.environ.get('CHARLIE_MUNGER_AGENT_ALIAS_ID', '')
        }
        
        for expert_name, expert_alias_id in expert_agents.items():
            if expert_alias_id:
                response = invoke_agent(expert_alias_id, f"分析股票 {ticker}")
                expert_responses.append({
                    "expert": expert_name,
                    "analysis": response
                })
        
        # 2. 调用分析Agent获取技术指标
        analysis_agents = {
            'ValuationAgent': os.environ.get('VALUATION_AGENT_ALIAS_ID', ''),
            'SentimentAgent': os.environ.get('SENTIMENT_AGENT_ALIAS_ID', ''),
            'FundamentalsAgent': os.environ.get('FUNDAMENTALS_AGENT_ALIAS_ID', ''),
            'TechnicalsAgent': os.environ.get('TECHNICALS_AGENT_ALIAS_ID', '')
        }
        
        analysis_responses = {}
        for analysis_name, analysis_alias_id in analysis_agents.items():
            if analysis_alias_id:
                response = invoke_agent(analysis_alias_id, f"分析股票 {ticker}")
                analysis_responses[analysis_name] = response
        
        # 3. 调用风险管理Agent评估风险
        risk_manager_alias_id = os.environ.get('RISK_MANAGER_AGENT_ALIAS_ID', '')
        risk_assessment = ""
        if risk_manager_alias_id:
            risk_assessment = invoke_agent(risk_manager_alias_id, f"评估股票 {ticker} 的风险")
        
        # 4. 整合所有信息
        combined_analysis = {
            "ticker": ticker,
            "expert_opinions": expert_responses,
            "technical_analysis": analysis_responses,
            "risk_assessment": risk_assessment
        }
        
        # 5. 生成最终决策
        final_decision = generate_decision(combined_analysis)
        
        return {
            "completion": final_decision
        }
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        return {
            "completion": f"处理请求时发生错误: {str(e)}"
        }

def extract_ticker(text):
    """
    从文本中提取股票代码
    """
    # 简单实现，实际应用中可能需要更复杂的逻辑
    common_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA']
    for ticker in common_tickers:
        if ticker in text.upper():
            return ticker
    return None

def invoke_agent(agent_alias_id, prompt):
    """
    调用Bedrock Agent
    """
    try:
        response = bedrock_agent_runtime.invoke_agent({
            'agentAliasId': agent_alias_id,
            'inputText': prompt,
            'enableTrace': True
        })
        return response.get('completion', '')
    except Exception as e:
        logger.error(f"调用Agent时出错: {str(e)}")
        return f"调用Agent时出错: {str(e)}"

def generate_decision(analysis):
    """
    基于所有分析生成最终决策
    """
    # 这里应该有更复杂的决策逻辑
    # 简单示例实现
    ticker = analysis.get('ticker', '')
    expert_opinions = analysis.get('expert_opinions', [])
    technical_analysis = analysis.get('technical_analysis', {})
    risk_assessment = analysis.get('risk_assessment', '')
    
    decision = f"## {ticker} 股票分析报告\n\n"
    
    # 添加专家意见
    decision += "### 投资专家观点\n\n"
    for expert in expert_opinions:
        decision += f"**{expert['expert']}**: {expert['analysis']}\n\n"
    
    # 添加技术分析
    decision += "### 技术分析\n\n"
    for analysis_type, analysis_result in technical_analysis.items():
        decision += f"**{analysis_type}**: {analysis_result}\n\n"
    
    # 添加风险评估
    decision += f"### 风险评估\n\n{risk_assessment}\n\n"
    
    # 添加最终建议
    decision += "### 投资建议\n\n"
    decision += "基于以上分析，我们的投资建议是: "
    # 这里应该有更复杂的逻辑来确定建议
    decision += "持有观望，等待更多市场信号。"
    
    return decision