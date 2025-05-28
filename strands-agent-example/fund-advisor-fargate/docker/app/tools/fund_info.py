from strands import tool
import boto3
from boto3.dynamodb.conditions import Key, Attr
import akshare as ak

kb_name = "fsi-fund-knowledge"

def get_table(table_name):
    """Helper function to get DynamoDB table
    Args:
        table_name: name of the table
    Returns:
        DynamoDB table resource
    """
    dynamodb = boto3.resource("dynamodb")
    smm_client = boto3.client("ssm")
    param_name = f"{kb_name}-{table_name}-table-name"
    
    try:
        table_param = smm_client.get_parameter(
            Name=param_name, WithDecryption=False
        )
        return dynamodb.Table(table_param["Parameter"]["Value"])
    except Exception as e:
        # 尝试旧格式的参数名称（兼容性）
        if table_name == "fund_basic_info":
            try:
                table_param = smm_client.get_parameter(
                    Name=f"{kb_name}-table-name", WithDecryption=False
                )
                return dynamodb.Table(table_param["Parameter"]["Value"])
            except Exception as e:
                raise Exception(f"无法获取表 {table_name}: {str(e)}")
        else:
            raise Exception(f"无法获取表 {table_name}: {str(e)}")

@tool
def get_fund_by_code(fund_code: str) -> dict:
    """Get fund details by fund code
    Args:
        fund_code: the code of the fund
    Returns:
        fund_details: the details of the fund in JSON format
    """
    try:
        fund_individual_basic_info_xq_df = ak.fund_individual_basic_info_xq(symbol=fund_code)
        return fund_individual_basic_info_xq_df.to_json(orient="records")
    except Exception:
        pass
    try:
        table = get_table("fund_basic_info")
        
        # Query using the primary key (fund_code)
        response = table.query(
            KeyConditionExpression=Key("fund_code").eq(fund_code)
        )
        
        if response["Items"]:
            return response["Items"]
        else:
            return f"No fund found with code {fund_code}"
    except Exception as e:
        return str(e)

@tool
def get_fund_by_name(fund_name: str) -> dict:
    """Get fund details by fund name
    Args:
        fund_name: the name of the fund
    Returns:
        fund_details: the details of the fund in JSON format
    """
    try:
        table = get_table("fund_basic_info")
        
        # Scan the table and filter by fund_name
        # Note: This is less efficient than querying by primary key
        response = table.scan(
            FilterExpression=Attr("fund_name").eq(fund_name)
        )
        
        if response["Items"]:
            return response["Items"]
        else:
            return f"No fund found with name {fund_name}"
    except Exception as e:
        return str(e)

@tool
def get_fund_details(fund_code: str = None, fund_name: str = None) -> dict:
    """Get the relevant details for a fund using either fund_code or fund_name
    Args:
        fund_code: the code of the fund (optional if fund_name is provided)
        fund_name: name of the fund (optional if fund_code is provided)
    Returns:
        fund_details: the details of the fund in JSON format
    """
    if not fund_code and not fund_name:
        return "Either fund_code or fund_name must be provided"
    try:
        fund_individual_basic_info_xq_df = ak.fund_individual_basic_info_xq(symbol=fund_code)
        return fund_individual_basic_info_xq_df.to_json(orient="records")
    except Exception:
        pass
    try:
        table = get_table("fund_basic_info")
        
        if fund_code and fund_name:
            # If both are provided, use get_item for exact match
            response = table.get_item(
                Key={"fund_code": fund_code, "fund_name": fund_name}
            )
            if "Item" in response:
                return response["Item"]
            else:
                return f"No fund found with code {fund_code} and name {fund_name}"
        
        elif fund_code:
            # If only fund_code is provided
            return get_fund_by_code(fund_code)
        
        else:
            # If only fund_name is provided
            return get_fund_by_name(fund_name)
            
    except Exception as e:
        return str(e)

@tool
def get_fund_manager_by_code(fund_code: str) -> dict:
    """Get fund manager information by fund code
    Args:
        fund_name: the code of the fund
    Returns:
        manager_details: the details of the fund manager in JSON format
    """
    try:
        table = get_table("fund_manager_info")
        
        # Scan the table and filter by fund_code (since fund_code is the sort key)
        response = table.scan(
            FilterExpression=Attr("fund_code").eq(fund_code)
        )
        
        if response["Items"]:
            return response["Items"]
        else:
            return f"No manager found for fund with code {fund_code}"
    except Exception as e:
        return str(e)

@tool
def get_fund_fees_by_code(fund_code: str) -> dict:
    """Get fund fee structure by fund code
    Args:
        fund_code: the code of the fund
    Returns:
        fee_details: the fee structure of the fund in JSON format
    """
    try:
        fund_fee_em_df_1 = ak.fund_fee_em(symbol=fund_code, indicator="认购费率")
        fund_fee_em_df_2 = ak.fund_fee_em(symbol=fund_code, indicator="赎回费率")
        return {"认购费率":fund_fee_em_df_1.to_string(), "赎回费率":fund_fee_em_df_2.to_string()}
    except Exception:
        pass
    try:
        table = get_table("fund_fee_structure")
        
        # Query using the primary key (fund_code)
        response = table.query(
            KeyConditionExpression=Key("fund_code").eq(fund_code)
        )
        
        if response["Items"]:
            return response["Items"]
        else:
            return f"No fee structure found for fund with code {fund_code}"
    except Exception as e:
        return str(e)

@tool
def get_fund_performance_by_code(fund_code: str, report_date: str = None) -> dict:
    """Get fund holdings by fund code and optionally by report date
    Args:
        fund_code: the code of the fund
        report_date: the report date of the holdings (optional)
    Returns:
        holdings_details: the holdings of the fund in JSON format
    """
    try:
        table = get_table("fund_performance")
        
        if report_date:
            # If report_date is provided, use get_item for exact match
            response = table.get_item(
                Key={"fund_code": fund_code, "report_date": report_date}
            )
            if "Item" in response:
                return response["Item"]
            else:
                fund_individual_achievement_xq_df = ak.fund_individual_achievement_xq(symbol=fund_code)
                return fund_individual_achievement_xq_df.to_dict(orient='records')
        else:
            # If only fund_code is provided, query all holdings for this fund
            response = table.query(
                KeyConditionExpression=Key("fund_code").eq(fund_code)
            )
            
            if response["Items"]:
                return response["Items"]
            else:
                fund_individual_achievement_xq_df = ak.fund_individual_achievement_xq(symbol=fund_code)
                return fund_individual_achievement_xq_df.to_dict(orient='records')
    except Exception as e:
        return str(e)
    

@tool
def get_fund_holdings_by_code(fund_code: str, report_date: str = None) -> dict:
    """Get fund holdings by fund code and optionally by report date
    Args:
        fund_code: the code of the fund
        report_date: the report date of the holdings (optional)
    Returns:
        holdings_details: the holdings of the fund in JSON format
    """
    try:
        fund_portfolio_hold_em_df = ak.fund_portfolio_hold_em(symbol=fund_code, date="2025")
        return fund_portfolio_hold_em_df[fund_portfolio_hold_em_df['季度'] == '2025年1季度股票投资明细'].head(10).to_dict(orient='records')
    except Exception:
        if not report_date:
            report_date = "2025-05-25"
        fund_individual_detail_hold_xq_df = ak.fund_individual_detail_hold_xq(symbol=fund_code, date=report_date)
        return fund_individual_detail_hold_xq_df.to_dict(orient='records')
    

@tool
def get_fund_profit_probability_by_code(fund_code: str) -> dict:
    """Get fund profit probability by fund code and optionally by report date
    Args:
        fund_code: the code of the fund
        report_date: the report date of the profit probability (optional)
    Returns:
        profit_probability_details: the profit probability of the fund in JSON format
    """
    try:
        fund_individual_profit_probability_xq_df = ak.fund_individual_profit_probability_xq(symbol=fund_code)
        return fund_individual_profit_probability_xq_df.to_dict(orient='records')
    except Exception:
        return {}
    
@tool
def get_fund_industry_by_code(fund_code: str) -> dict:
    """Get fund industry allocation by fund code
    Args:
        fund_code: the code of the fund
    Returns:
        industry_allocation: the industry allocation of the fund in JSON format
    """
    try:
        fund_industry_allocation_df  = ak.fund_portfolio_industry_allocation_em(symbol=fund_code, date="2025")
        return fund_industry_allocation_df.head(5).to_dict(orient='records')
    except Exception:
        return {}
    
@tool
def get_fund_individual_analysis_by_code(fund_code: str) -> dict:
    """Get fund individual analysis by fund code
    Args:
        fund_code: the code of the fund
    Returns:
        individual_analysis: the individual analysis of the fund in JSON format
    """
    try:
        fund_individual_analysis_df = ak.fund_individual_analysis_xq(symbol=fund_code)
        return fund_individual_analysis_df.to_dict(orient='records')
    except Exception as e:
        return {"error": str(e)}

@tool
def get_fund_search_results(query: str, fund_type: str = None) -> dict:
    """Search for funds based on a query string and optionally filter by fund type
    Args:
        query: the search query string
        fund_type: optional filter by fund type (e.g., '债券型', '混合型', '指数型', '货币型')
    Returns:
        search_results: the search results in JSON format, sorted by ytd_return (year-to-date return)
        in descending order and randomly selecting 20 from the top 100
    """
    try:
        import duckdb
        import pandas as pd
        import random
        from pathlib import Path
        
        # 获取CSV文件的绝对路径
        current_dir = Path(__file__).parent
        csv_path = current_dir / "data" / "fund_performance_all.csv"
        
        # 构建SQL查询
        sql_query = f"""
            SELECT * FROM read_csv('{csv_path}', AUTO_DETECT=TRUE)
            WHERE 1=1
        """
        
        # 添加模糊搜索条件
        if query:
            sql_query += f"""
                AND (
                    fund_code LIKE '%{query}%' OR
                    fund_name LIKE '%{query}%'
                )
            """
        
        # 如果提供了基金类型，添加筛选条件
        if fund_type:
            sql_query += f"""
                AND fund_type LIKE '%{fund_type}%'
            """
        
        # 按照ytd_return降序排序并限制结果为前100个
        sql_query += """
            ORDER BY CAST(ytd_return AS FLOAT) DESC
            LIMIT 100
        """
        
        # 执行查询
        result = duckdb.sql(sql_query).df()
        
        # 如果结果少于20个，返回所有结果
        if len(result) <= 20:
            return result.to_dict(orient='records')
        
        # 从前100个结果中随机选择20个
        random_indices = random.sample(range(len(result)), 20)
        random_results = result.iloc[random_indices]
        
        # 将结果转换为字典列表
        return random_results.to_dict(orient='records')
    except Exception as e:
        return {"error": str(e)}