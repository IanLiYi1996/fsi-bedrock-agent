import json
import logging
import boto3
import os
import uuid

# 配置日志
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 初始化Bedrock客户端
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')

def handler(event, context):
    """
    Agent Action Group Lambda函数
    处理来自投资组合管理Agent的请求，协调多个Agent的工作
    """
    logger.info(f"收到的事件: {json.dumps(event)}")
    
    try:
        # 解析API请求
        api_path = event.get('apiPath', '')
        parameters = event.get('parameters', {})
        request_body = event.get('requestBody', {})
        http_method = event.get('httpMethod', 'POST')
        action_group = event.get('actionGroup', 'agent-collaboration')
        
        # 处理不同的API路径
        if api_path == '/analyzeFund':
            # 从请求体中获取基金代码
            fund_code = None
            if request_body:
                fund_code = request_body.get('fundCode', '')
            
            # 如果请求体中没有基金代码，尝试从参数中获取
            if not fund_code and parameters:
                fund_code = parameters.get('fundCode', '')
            
            # 如果仍然没有基金代码，尝试从事件中提取
            if not fund_code:
                # 尝试从事件中的其他位置提取基金代码
                input_text = event.get('text', '')
                if input_text:
                    fund_code = extract_fund_code(input_text)
            
            if not fund_code:
                return format_response(
                    action_group=action_group,
                    api_path=api_path,
                    http_method=http_method,
                    http_status_code=400,
                    response_body={
                        "message": "请提供有效的基金代码，例如 '000001'、'110022' 或 '000961'。"
                    }
                )
            
            # 1. 调用专家Agent获取分析
            expert_responses = []
            expert_agents = {
                'FundStrategyAgent': os.environ.get('FUND_STRATEGY_AGENT_ALIAS_ID', ''),
                'AssetAllocationAgent': os.environ.get('ASSET_ALLOCATION_AGENT_ALIAS_ID', ''),
                'MarketTrendAgent': os.environ.get('MARKET_TREND_AGENT_ALIAS_ID', '')
            }
            
            for expert_name, expert_alias_id in expert_agents.items():
                if expert_alias_id:
                    response = invoke_agent(expert_alias_id, f"分析基金 {fund_code}")
                    expert_responses.append({
                        "expert": expert_name,
                        "analysis": response
                    })
            
            # 2. 调用分析Agent获取技术指标
            analysis_agents = {
                'PerformanceAgent': os.environ.get('PERFORMANCE_AGENT_ALIAS_ID', ''),
                'HoldingsAgent': os.environ.get('HOLDINGS_AGENT_ALIAS_ID', ''),
                'ManagerAgent': os.environ.get('MANAGER_AGENT_ALIAS_ID', ''),
                'FeesAgent': os.environ.get('FEES_AGENT_ALIAS_ID', '')
            }
            
            analysis_responses = {}
            for analysis_name, analysis_alias_id in analysis_agents.items():
                if analysis_alias_id:
                    response = invoke_agent(analysis_alias_id, f"分析基金 {fund_code}")
                    analysis_responses[analysis_name] = response
            
            # 3. 整合所有信息
            combined_analysis = {
                "fundCode": fund_code,
                "expert_opinions": expert_responses,
                "analysis_results": analysis_responses
            }
            
            # 4. 生成最终决策
            final_decision = generate_fund_analysis(combined_analysis)
            
            # 返回Action Group格式的结果
            return format_response(
                action_group=action_group,
                api_path=api_path,
                http_method=http_method,
                http_status_code=200,
                response_body={
                    "analysis": final_decision
                }
            )
        elif api_path == '/recommendFunds':
            # 从请求体中获取用户偏好
            risk_preference = None
            investment_horizon = None
            preferred_industry = None
            
            if request_body:
                risk_preference = request_body.get('riskPreference', '')
                investment_horizon = request_body.get('investmentHorizon', '')
                preferred_industry = request_body.get('preferredIndustry', '')
            
            # 如果请求体中没有用户偏好，尝试从参数中获取
            if not risk_preference and parameters:
                risk_preference = parameters.get('riskPreference', '')
            
            if not investment_horizon and parameters:
                investment_horizon = parameters.get('investmentHorizon', '')
            
            if not preferred_industry and parameters:
                preferred_industry = parameters.get('preferredIndustry', '')
            
            # 1. 调用用户画像Agent分析用户需求
            user_profile_alias_id = os.environ.get('USER_PROFILE_AGENT_ALIAS_ID', '')
            user_profile = ""
            if user_profile_alias_id:
                user_profile_prompt = f"分析用户投资偏好：风险偏好 {risk_preference or '未指定'}，投资期限 {investment_horizon or '未指定'}，偏好行业 {preferred_industry or '未指定'}"
                user_profile = invoke_agent(user_profile_alias_id, user_profile_prompt)
            
            # 2. 调用基金筛选Agent筛选基金
            fund_selector_alias_id = os.environ.get('FUND_SELECTOR_AGENT_ALIAS_ID', '')
            fund_recommendations = ""
            if fund_selector_alias_id:
                fund_selector_prompt = f"根据用户画像推荐基金：{user_profile}"
                fund_recommendations = invoke_agent(fund_selector_alias_id, fund_selector_prompt)
            
            # 3. 调用专家Agent评估推荐结果
            expert_opinions = []
            expert_agents = {
                'FundStrategyAgent': os.environ.get('FUND_STRATEGY_AGENT_ALIAS_ID', ''),
                'AssetAllocationAgent': os.environ.get('ASSET_ALLOCATION_AGENT_ALIAS_ID', ''),
                'MarketTrendAgent': os.environ.get('MARKET_TREND_AGENT_ALIAS_ID', '')
            }
            
            for expert_name, expert_alias_id in expert_agents.items():
                if expert_alias_id:
                    expert_prompt = f"评估以下基金推荐是否符合用户需求：\n用户画像：{user_profile}\n推荐基金：{fund_recommendations}"
                    response = invoke_agent(expert_alias_id, expert_prompt)
                    expert_opinions.append({
                        "expert": expert_name,
                        "opinion": response
                    })
            
            # 4. 整合所有信息
            combined_recommendation = {
                "user_profile": user_profile,
                "fund_recommendations": fund_recommendations,
                "expert_opinions": expert_opinions
            }
            
            # 5. 生成最终推荐
            final_recommendation = generate_fund_recommendation(combined_recommendation)
            
            # 返回Action Group格式的结果
            return format_response(
                action_group=action_group,
                api_path=api_path,
                http_method=http_method,
                http_status_code=200,
                response_body={
                    "recommendation": final_recommendation
                }
            )
        else:
            # 未知的API路径
            return format_response(
                action_group=action_group,
                api_path=api_path,
                http_method=http_method,
                http_status_code=400,
                response_body={
                    "message": f"不支持的API路径: {api_path}"
                }
            )
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        error_message = f"处理请求时发生错误: {str(e)}"
        logger.error(error_message)
        
        # 返回错误信息
        return format_response(
            action_group="agent-collaboration",
            api_path=event.get('apiPath', '/analyzeFund'),
            http_method=event.get('httpMethod', 'POST'),
            http_status_code=500,
            response_body={
                "message": error_message
            }
        )

def format_response(action_group, api_path, http_method, http_status_code, response_body):
    """
    格式化Lambda响应，符合Amazon Bedrock Agent Action Group的预期格式
    
    Args:
        action_group (str): Action Group名称
        api_path (str): API路径
        http_method (str): HTTP方法
        http_status_code (int): HTTP状态码
        response_body (dict): 响应体
    """
    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": action_group,
            "apiPath": api_path,
            "httpMethod": http_method,
            "httpStatusCode": http_status_code,
            "responseBody": {
                "application/json": response_body
            }
        }
    }

def extract_fund_code(text):
    """
    从文本中提取基金代码
    """
    # 简单实现，实际应用中可能需要更复杂的逻辑
    common_fund_codes = ['000001', '110022', '000961', '000198', '000617', '001156', '001975', '003096', '005827', '001714']
    for fund_code in common_fund_codes:
        if fund_code in text:
            return fund_code
    return None

def invoke_agent(agent_alias_id, prompt):
    """
    调用Bedrock Agent
    
    Args:
        agent_alias_id (str): Agent Alias ID
        prompt (str): 提示文本
    """
    try:
        # 生成随机会话ID
        session_id = str(uuid.uuid4())
        
        # 记录调用信息
        logger.info(f"调用Agent，alias_id: {agent_alias_id}, prompt: {prompt}")
        
        # 调用Agent
        response = bedrock_agent_runtime.invoke_agent(
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=prompt,
            enableTrace=True
        )
        
        # 获取完成结果
        completion = response.get('completion', '')
        logger.info(f"Agent响应: {completion[:100]}...")  # 只记录前100个字符
        
        return completion
    except Exception as e:
        logger.error(f"调用Agent时出错: {str(e)}")
        return f"调用Agent时出错: {str(e)}"

def generate_fund_analysis(analysis):
    """
    基于所有分析生成最终基金分析报告
    """
    # 这里应该有更复杂的决策逻辑
    # 简单示例实现
    fund_code = analysis.get('fundCode', '')
    expert_opinions = analysis.get('expert_opinions', [])
    analysis_results = analysis.get('analysis_results', {})
    
    report = f"## 基金 {fund_code} 分析报告\n\n"
    
    # 添加专家意见
    report += "### 专家观点\n\n"
    for expert in expert_opinions:
        report += f"**{expert['expert']}**: {expert['analysis']}\n\n"
    
    # 添加分析结果
    report += "### 分析结果\n\n"
    for analysis_type, analysis_result in analysis_results.items():
        report += f"**{analysis_type}**: {analysis_result}\n\n"
    
    # 添加最终建议
    report += "### 投资建议\n\n"
    report += "基于以上分析，我们的投资建议是: "
    # 这里应该有更复杂的逻辑来确定建议
    report += "该基金具有良好的投资价值，建议适量配置。请根据个人风险承受能力和投资目标做出最终决策。"
    
    return report

def generate_fund_recommendation(recommendation):
    """
    基于所有信息生成最终基金推荐报告
    """
    # 这里应该有更复杂的决策逻辑
    # 简单示例实现
    user_profile = recommendation.get('user_profile', '')
    fund_recommendations = recommendation.get('fund_recommendations', '')
    expert_opinions = recommendation.get('expert_opinions', [])
    
    report = "## 基金推荐报告\n\n"
    
    # 添加用户画像
    report += "### 用户投资画像\n\n"
    report += f"{user_profile}\n\n"
    
    # 添加基金推荐
    report += "### 推荐基金\n\n"
    report += f"{fund_recommendations}\n\n"
    
    # 添加专家意见
    report += "### 专家评估\n\n"
    for expert in expert_opinions:
        report += f"**{expert['expert']}**: {expert['opinion']}\n\n"
    
    # 添加最终建议
    report += "### 投资组合建议\n\n"
    report += "基于您的投资偏好和目标，我们建议您考虑以上推荐的基金产品。请根据个人风险承受能力和投资目标做出最终决策。"
    
    return report