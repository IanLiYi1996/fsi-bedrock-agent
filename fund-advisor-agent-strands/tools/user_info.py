from strands import tool
import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
from datetime import datetime

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
        raise Exception(f"无法获取表 {table_name}: {str(e)}")

@tool
def get_user_holdings(user_id: str) -> dict:
    """获取用户的基金持仓信息
    Args:
        user_id: 用户ID
    Returns:
        holdings: 用户持仓信息的JSON格式
    """
    try:
        table = get_table("user_holdings")
        
        # 使用主键(user_id)查询
        response = table.query(
            KeyConditionExpression=Key("user_id").eq(user_id)
        )
        
        if response["Items"]:
            return response["Items"]
        else:
            return f"未找到用户 {user_id} 的持仓信息"
    except Exception as e:
        return str(e)

@tool
def get_user_fund_holding(user_id: str, fund_code: str) -> dict:
    """获取用户特定基金的持仓信息
    Args:
        user_id: 用户ID
        fund_code: 基金代码
    Returns:
        holding: 特定基金持仓信息的JSON格式
    """
    try:
        table = get_table("user_holdings")
        
        # 使用主键(user_id)和排序键(fund_code)查询
        response = table.get_item(
            Key={
                "user_id": user_id,
                "fund_code": fund_code
            }
        )
        
        if "Item" in response:
            return response["Item"]
        else:
            return f"未找到用户 {user_id} 持有的基金 {fund_code}"
    except Exception as e:
        return str(e)

@tool
def add_user_holding(user_id: str, fund_code: str, fund_name: str, 
                    holding_amount: float, purchase_date: str, 
                    purchase_price: float) -> dict:
    """添加用户基金持仓信息
    Args:
        user_id: 用户ID
        fund_code: 基金代码
        fund_name: 基金名称
        holding_amount: 持有份额
        purchase_date: 购买日期 (格式: YYYY-MM-DD)
        purchase_price: 购买价格
    Returns:
        result: 操作结果
    """
    try:
        table = get_table("user_holdings")
        
        # 计算当前价值和盈亏（实际应用中应该从实时数据获取）
        current_value = holding_amount * purchase_price  # 示例，实际应该获取最新净值
        profit_loss = 0.0  # 示例，实际应该计算盈亏
        
        # 创建项目
        item = {
            "user_id": user_id,
            "fund_code": fund_code,
            "fund_name": fund_name,
            "holding_amount": holding_amount,
            "purchase_date": purchase_date,
            "purchase_price": purchase_price,
            "current_value": current_value,
            "profit_loss": profit_loss,
            "last_updated": datetime.now().isoformat()
        }
        
        # 添加到DynamoDB
        table.put_item(Item=item)
        
        return {"status": "success", "message": f"成功添加用户 {user_id} 的基金 {fund_code} 持仓信息"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
def update_user_holding(user_id: str, fund_code: str, 
                       holding_amount: float = None, 
                       current_value: float = None,
                       profit_loss: float = None) -> dict:
    """更新用户基金持仓信息
    Args:
        user_id: 用户ID
        fund_code: 基金代码
        holding_amount: 持有份额 (可选)
        current_value: 当前价值 (可选)
        profit_loss: 盈亏情况 (可选)
    Returns:
        result: 操作结果
    """
    try:
        table = get_table("user_holdings")
        
        # 检查项目是否存在
        response = table.get_item(
            Key={
                "user_id": user_id,
                "fund_code": fund_code
            }
        )
        
        if "Item" not in response:
            return {"status": "error", "message": f"未找到用户 {user_id} 持有的基金 {fund_code}"}
        
        # 构建更新表达式
        update_expression = "SET last_updated = :updated"
        expression_values = {
            ":updated": datetime.now().isoformat()
        }
        
        if holding_amount is not None:
            update_expression += ", holding_amount = :amount"
            expression_values[":amount"] = holding_amount
            
        if current_value is not None:
            update_expression += ", current_value = :value"
            expression_values[":value"] = current_value
            
        if profit_loss is not None:
            update_expression += ", profit_loss = :profit"
            expression_values[":profit"] = profit_loss
        
        # 更新项目
        table.update_item(
            Key={
                "user_id": user_id,
                "fund_code": fund_code
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values
        )
        
        return {"status": "success", "message": f"成功更新用户 {user_id} 的基金 {fund_code} 持仓信息"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
def delete_user_holding(user_id: str, fund_code: str) -> dict:
    """删除用户基金持仓信息
    Args:
        user_id: 用户ID
        fund_code: 基金代码
    Returns:
        result: 操作结果
    """
    try:
        table = get_table("user_holdings")
        
        # 删除项目
        table.delete_item(
            Key={
                "user_id": user_id,
                "fund_code": fund_code
            }
        )
        
        return {"status": "success", "message": f"成功删除用户 {user_id} 的基金 {fund_code} 持仓信息"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
def get_user_portfolio_summary(user_id: str) -> dict:
    """获取用户投资组合摘要
    Args:
        user_id: 用户ID
    Returns:
        summary: 用户投资组合摘要的JSON格式
    """
    try:
        holdings = get_user_holdings(user_id)
        
        if isinstance(holdings, str):  # 错误消息
            return holdings
            
        # 计算总资产和总盈亏
        total_value = sum(item.get("current_value", 0) for item in holdings)
        total_profit_loss = sum(item.get("profit_loss", 0) for item in holdings)
        
        # 计算每个基金的占比
        for item in holdings:
            if "current_value" in item and total_value > 0:
                item["percentage"] = (item["current_value"] / total_value) * 100
            else:
                item["percentage"] = 0
                
        return {
            "user_id": user_id,
            "total_value": total_value,
            "total_profit_loss": total_profit_loss,
            "holdings_count": len(holdings),
            "holdings": holdings
        }
    except Exception as e:
        return str(e)