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
    基金搜索Lambda函数
    处理来自基金筛选Agent的请求，搜索符合条件的基金
    """
    logger.info(f"收到的事件: {json.dumps(event)}")
    
    try:
        # 解析API请求
        api_path = event.get('apiPath', '')
        parameters = event.get('parameters', {})
        request_body = event.get('requestBody', {})
        http_method = event.get('httpMethod', 'POST')
        action_group = event.get('actionGroup', 'fund-search')
        
        # 处理不同的API路径
        if api_path == '/searchFunds':
            # 从请求体中获取搜索条件
            fund_type = None
            risk_level = None
            industry = None
            investment_horizon = None
            
            if request_body:
                fund_type = request_body.get('fundType', '')
                risk_level = request_body.get('riskLevel', '')
                industry = request_body.get('industry', '')
                investment_horizon = request_body.get('investmentHorizon', '')
            
            # 如果请求体中没有搜索条件，尝试从参数中获取
            if not fund_type and parameters:
                fund_type = parameters.get('fundType', '')
            
            if not risk_level and parameters:
                risk_level = parameters.get('riskLevel', '')
            
            if not industry and parameters:
                industry = parameters.get('industry', '')
            
            if not investment_horizon and parameters:
                investment_horizon = parameters.get('investmentHorizon', '')
            
            # 构建搜索参数
            search_params = {}
            if fund_type:
                search_params['fundType'] = fund_type
            if risk_level:
                search_params['riskLevel'] = risk_level
            if industry:
                search_params['industry'] = industry
            if investment_horizon:
                search_params['investmentHorizon'] = investment_horizon
            
            # 调用基金数据API搜索基金
            search_results = search_funds(search_params)
            
            # 返回Action Group格式的结果
            return format_response(
                action_group=action_group,
                api_path=api_path,
                http_method=http_method,
                http_status_code=200,
                response_body={
                    "funds": search_results.get("funds", []),
                    "count": search_results.get("count", 0),
                    "searchCriteria": search_params
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
            action_group="fund-search",
            api_path=event.get('apiPath', '/searchFunds'),
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

def search_funds(search_params):
    """
    搜索符合条件的基金
    
    Args:
        search_params (dict): 搜索条件
    """
    try:
        # 构建查询参数
        query_params = ""
        for key, value in search_params.items():
            if value:
                query_params += f"&{key}={value}"
        
        if query_params:
            query_params = "?" + query_params[1:]  # 移除第一个&符号
        
        # 调用基金数据API
        # 注意：在实际环境中，这里应该调用真实的API端点
        # 这里为了演示，我们模拟API调用结果
        
        # 模拟基金数据
        funds = [
            {
                "fundCode": "000001",
                "name": "华夏成长混合",
                "type": "混合型",
                "riskLevel": "中高",
                "company": "华夏基金",
                "industry": "多行业"
            },
            {
                "fundCode": "110022",
                "name": "易方达消费行业股票",
                "type": "股票型",
                "riskLevel": "高",
                "company": "易方达基金",
                "industry": "消费"
            },
            {
                "fundCode": "000961",
                "name": "天弘沪深300指数",
                "type": "指数型",
                "riskLevel": "中高",
                "company": "天弘基金",
                "industry": "多行业"
            },
            {
                "fundCode": "000198",
                "name": "中银纯债债券A",
                "type": "债券型",
                "riskLevel": "中低",
                "company": "中银基金",
                "industry": "多行业"
            },
            {
                "fundCode": "000617",
                "name": "易方达货币市场基金A",
                "type": "货币型",
                "riskLevel": "低",
                "company": "易方达基金",
                "industry": "多行业"
            },
            {
                "fundCode": "001156",
                "name": "申万菱信新能源汽车主题灵活配置混合",
                "type": "混合型",
                "riskLevel": "中高",
                "company": "申万菱信基金",
                "industry": "新能源汽车"
            },
            {
                "fundCode": "001975",
                "name": "景顺长城环保优势股票",
                "type": "股票型",
                "riskLevel": "高",
                "company": "景顺长城基金",
                "industry": "环保"
            },
            {
                "fundCode": "003096",
                "name": "中欧医疗健康混合A",
                "type": "混合型",
                "riskLevel": "中高",
                "company": "中欧基金",
                "industry": "医疗健康"
            },
            {
                "fundCode": "005827",
                "name": "易方达蓝筹精选混合",
                "type": "混合型",
                "riskLevel": "中高",
                "company": "易方达基金",
                "industry": "多行业"
            },
            {
                "fundCode": "001714",
                "name": "工银瑞信文体产业股票A",
                "type": "股票型",
                "riskLevel": "高",
                "company": "工银瑞信基金",
                "industry": "文化传媒"
            }
        ]
        
        # 筛选基金
        filtered_funds = []
        for fund in funds:
            match = True
            
            if search_params.get('fundType') and fund["type"] != search_params.get('fundType'):
                match = False
            
            if search_params.get('riskLevel') and fund["riskLevel"] != search_params.get('riskLevel'):
                match = False
            
            if search_params.get('industry') and fund["industry"] != search_params.get('industry'):
                match = False
            
            # 根据投资期限筛选基金类型
            if search_params.get('investmentHorizon'):
                if search_params.get('investmentHorizon') == "短期" and fund["type"] not in ["货币型", "债券型"]:
                    match = False
                elif search_params.get('investmentHorizon') == "中期" and fund["type"] not in ["债券型", "混合型"]:
                    match = False
                elif search_params.get('investmentHorizon') == "长期" and fund["type"] not in ["混合型", "股票型", "指数型"]:
                    match = False
            
            if match:
                filtered_funds.append(fund)
        
        return {
            "funds": filtered_funds,
            "count": len(filtered_funds)
        }
    except Exception as e:
        logger.error(f"搜索基金时出错: {str(e)}")
        return {
            "funds": [],
            "count": 0,
            "error": str(e)
        }