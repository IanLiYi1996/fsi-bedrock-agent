from strands import tool
from typing import Optional, List, Dict, Any
import random
import sys
import os

# 添加项目根目录到Python路径，以便导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 导入备用基金数据
from tools.fund_data import backup_funds

@tool
def search_funds(
    fund_type: Optional[str] = None, 
    risk_level: Optional[str] = None, 
    industry: Optional[str] = None, 
    investment_horizon: Optional[str] = None
) -> Dict[str, Any]:
    """
    搜索符合条件的基金
    
    Args:
        fund_type: 基金类型（股票型、债券型、混合型、货币型等）
        risk_level: 风险等级（低、中低、中、中高、高）
        industry: 行业主题（科技、医疗、消费等）
        investment_horizon: 投资期限（短期、中期、长期）
    """
    try:
        # 筛选基金
        filtered_funds = []
        for fund_code, fund_info in backup_funds.items():
            match = True
            
            # 根据基金类型筛选
            if fund_type and fund_info["type"] != fund_type:
                match = False
            
            # 根据风险等级筛选
            if risk_level and fund_info["risk_level"] != risk_level:
                match = False
            
            # 根据行业主题筛选
            if industry and fund_info.get("industry", "多行业") != industry and "多行业" not in fund_info.get("industry", "多行业"):
                match = False
            
            # 根据投资期限筛选基金类型
            if investment_horizon:
                if investment_horizon == "短期" and fund_info["type"] not in ["货币型", "债券型"]:
                    match = False
                elif investment_horizon == "中期" and fund_info["type"] not in ["债券型", "混合型"]:
                    match = False
                elif investment_horizon == "长期" and fund_info["type"] not in ["混合型", "股票型", "指数型"]:
                    match = False
            
            if match:
                filtered_funds.append({
                    "fundCode": fund_code,
                    "name": fund_info["name"],
                    "type": fund_info["type"],
                    "riskLevel": fund_info["risk_level"],
                    "company": fund_info.get("company", "未知"),
                    "industry": fund_info.get("industry", "多行业")
                })
        
        # 如果没有找到匹配的基金，生成一些模拟数据
        if not filtered_funds:
            # 根据条件生成模拟基金
            fund_types = ["股票型", "债券型", "混合型", "货币型", "指数型"]
            risk_levels = ["低", "中低", "中", "中高", "高"]
            companies = ["华夏基金", "易方达基金", "天弘基金", "中银基金", "工银瑞信基金", "南方基金", "嘉实基金", "博时基金"]
            industries = ["科技", "医疗健康", "消费", "新能源", "金融", "环保", "文化传媒", "多行业"]
            
            # 根据输入条件确定基金类型
            selected_fund_types = [fund_type] if fund_type else fund_types
            if investment_horizon == "短期":
                selected_fund_types = [ft for ft in selected_fund_types if ft in ["货币型", "债券型"]]
            elif investment_horizon == "中期":
                selected_fund_types = [ft for ft in selected_fund_types if ft in ["债券型", "混合型"]]
            elif investment_horizon == "长期":
                selected_fund_types = [ft for ft in selected_fund_types if ft in ["混合型", "股票型", "指数型"]]
            
            # 根据输入条件确定风险等级
            selected_risk_levels = [risk_level] if risk_level else risk_levels
            
            # 根据输入条件确定行业
            selected_industries = [industry] if industry else industries
            
            # 生成5-10个模拟基金
            num_funds = random.randint(5, 10)
            for i in range(num_funds):
                fund_type = random.choice(selected_fund_types)
                
                # 根据基金类型确定风险等级
                if fund_type == "货币型":
                    fund_risk_level = "低"
                elif fund_type == "债券型":
                    fund_risk_level = "中低"
                elif fund_type == "混合型":
                    fund_risk_level = "中高"
                elif fund_type == "股票型" or fund_type == "指数型":
                    fund_risk_level = "高"
                else:
                    fund_risk_level = random.choice(selected_risk_levels)
                
                # 如果指定了风险等级，确保匹配
                if risk_level and fund_risk_level != risk_level:
                    continue
                
                fund_industry = random.choice(selected_industries)
                fund_company = random.choice(companies)
                
                # 生成基金代码和名称
                fund_code = f"{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}"
                fund_name = f"{fund_company.split('基金')[0]}{fund_industry}{fund_type}"
                
                filtered_funds.append({
                    "fundCode": fund_code,
                    "name": fund_name,
                    "type": fund_type,
                    "riskLevel": fund_risk_level,
                    "company": fund_company,
                    "industry": fund_industry
                })
        
        return {
            "status": "success",
            "content": [
                {
                    "json": {
                        "funds": filtered_funds,
                        "count": len(filtered_funds)
                    }
                }
            ]
        }
    except Exception as e:
        return {
            "status": "error",
            "content": [
                {"text": f"搜索基金出错: {str(e)}"}
            ]
        }
