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

@tool
def get_user_profile(user_id: str) -> dict:
    """获取用户的身份信息
    Args:
        user_id: 用户ID
    Returns:
        profile: 用户身份信息的JSON格式
    """
    try:
        table = get_table("user_profile")
        
        # 使用主键(user_id)查询
        response = table.get_item(
            Key={
                "user_id": user_id
            }
        )
        
        if "Item" in response:
            return response["Item"]
        else:
            return f"未找到用户 {user_id} 的身份信息"
    except Exception as e:
        return str(e)

@tool
def create_user_profile(user_id: str, name: str, age: int, risk_preference: str,
                       investment_horizon: int, investment_goal: str,
                       annual_income: float = None, total_assets: float = None) -> dict:
    """创建用户身份信息
    Args:
        user_id: 用户ID
        name: 用户姓名
        age: 用户年龄
        risk_preference: 风险偏好（低风险、中等风险、高风险）
        investment_horizon: 投资年限（年）
        investment_goal: 投资目标
        annual_income: 年收入（可选）
        total_assets: 总资产（可选）
    Returns:
        result: 操作结果
    """
    try:
        table = get_table("user_profile")
        
        # 检查用户是否已存在
        response = table.get_item(
            Key={
                "user_id": user_id
            }
        )
        
        if "Item" in response:
            return {"status": "error", "message": f"用户 {user_id} 已存在"}
        
        # 创建项目
        item = {
            "user_id": user_id,
            "name": name,
            "age": age,
            "risk_preference": risk_preference,
            "investment_horizon": investment_horizon,
            "investment_goal": investment_goal,
            "last_updated": datetime.now().isoformat()
        }
        
        if annual_income is not None:
            item["annual_income"] = annual_income
            
        if total_assets is not None:
            item["total_assets"] = total_assets
        
        # 添加到DynamoDB
        table.put_item(Item=item)
        
        return {"status": "success", "message": f"成功创建用户 {user_id} 的身份信息"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
def update_user_profile(user_id: str, name: str = None, age: int = None,
                       risk_preference: str = None, investment_horizon: int = None,
                       investment_goal: str = None, annual_income: float = None,
                       total_assets: float = None) -> dict:
    """更新用户身份信息
    Args:
        user_id: 用户ID
        name: 用户姓名（可选）
        age: 用户年龄（可选）
        risk_preference: 风险偏好（可选）
        investment_horizon: 投资年限（可选）
        investment_goal: 投资目标（可选）
        annual_income: 年收入（可选）
        total_assets: 总资产（可选）
    Returns:
        result: 操作结果
    """
    try:
        table = get_table("user_profile")
        
        # 检查用户是否存在
        response = table.get_item(
            Key={
                "user_id": user_id
            }
        )
        
        if "Item" not in response:
            return {"status": "error", "message": f"未找到用户 {user_id}"}
        
        # 构建更新表达式
        update_expression = "SET last_updated = :updated"
        expression_values = {
            ":updated": datetime.now().isoformat()
        }
        
        if name is not None:
            update_expression += ", #name = :name"
            expression_values[":name"] = name
            
        if age is not None:
            update_expression += ", age = :age"
            expression_values[":age"] = age
            
        if risk_preference is not None:
            update_expression += ", risk_preference = :risk"
            expression_values[":risk"] = risk_preference
            
        if investment_horizon is not None:
            update_expression += ", investment_horizon = :horizon"
            expression_values[":horizon"] = investment_horizon
            
        if investment_goal is not None:
            update_expression += ", investment_goal = :goal"
            expression_values[":goal"] = investment_goal
            
        if annual_income is not None:
            update_expression += ", annual_income = :income"
            expression_values[":income"] = annual_income
            
        if total_assets is not None:
            update_expression += ", total_assets = :assets"
            expression_values[":assets"] = total_assets
        
        # 更新项目
        table.update_item(
            Key={
                "user_id": user_id
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ExpressionAttributeNames={
                "#name": "name"  # name 是 DynamoDB 的保留字，需要使用表达式属性名
            } if name is not None else {}
        )
        
        return {"status": "success", "message": f"成功更新用户 {user_id} 的身份信息"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@tool
def get_user_comprehensive_info(user_id: str) -> dict:
    """获取用户的综合信息（包括身份信息和投资组合）
    Args:
        user_id: 用户ID
    Returns:
        info: 用户综合信息的JSON格式
    """
    try:
        # 获取用户身份信息
        profile = get_user_profile(user_id)
        if isinstance(profile, str):  # 错误消息
            return {"status": "error", "message": profile}
            
        # 获取用户投资组合摘要
        portfolio = get_user_portfolio_summary(user_id)
        if isinstance(portfolio, str):  # 错误消息
            portfolio = {"status": "error", "message": portfolio}
            
        # 合并信息
        return {
            "user_id": user_id,
            "profile": profile,
            "portfolio": portfolio
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}