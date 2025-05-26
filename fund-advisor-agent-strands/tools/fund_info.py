from strands import tool
import boto3
from boto3.dynamodb.conditions import Key, Attr

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
        fund_code: the code of the fund
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
def get_fund_holdings_by_code(fund_code: str, report_date: str = None) -> dict:
    """Get fund holdings by fund code and optionally by report date
    Args:
        fund_code: the code of the fund
        report_date: the report date of the holdings (optional)
    Returns:
        holdings_details: the holdings of the fund in JSON format
    """
    try:
        table = get_table("fund_holdings")
        
        if report_date:
            # If report_date is provided, use get_item for exact match
            response = table.get_item(
                Key={"fund_code": fund_code, "report_date": report_date}
            )
            if "Item" in response:
                return response["Item"]
            else:
                return f"No holdings found for fund with code {fund_code} on date {report_date}"
        else:
            # If only fund_code is provided, query all holdings for this fund
            response = table.query(
                KeyConditionExpression=Key("fund_code").eq(fund_code)
            )
            
            if response["Items"]:
                return response["Items"]
            else:
                return f"No holdings found for fund with code {fund_code}"
    except Exception as e:
        return str(e)