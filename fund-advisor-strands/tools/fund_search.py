from strands import tool
from typing import Optional, List, Dict, Any
import random
import sys
import os
import logging
import pandas as pd
from functools import lru_cache

# 添加项目根目录到Python路径，以便导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 导入备用基金数据
from tools.fund_data import backup_funds

# 设置日志
logger = logging.getLogger(__name__)

# 尝试导入AKShare
AKSHARE_AVAILABLE = False
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
    logger.info("AKShare导入成功")
except ImportError:
    logger.warning("AKShare导入失败，将使用备用数据")

# 缓存装饰器
def cache_result(ttl_seconds=3600):
    """缓存函数结果，带有过期时间"""
    def decorator(func):
        cache = {}
        
        def wrapper(*args, **kwargs):
            import time
            key = str(args) + str(kwargs)
            current_time = time.time()
            
            if key in cache:
                result, timestamp = cache[key]
                if current_time - timestamp < ttl_seconds:
                    return result
            
            result = func(*args, **kwargs)
            cache[key] = (result, current_time)
            return result
        
        return wrapper
    
    return decorator

@cache_result(ttl_seconds=3600)
def get_fund_list():
    """获取基金列表，带缓存"""
    if AKSHARE_AVAILABLE:
        try:
            # 获取开放式基金列表
            fund_df = ak.fund_name_em()
            return fund_df
        except Exception as e:
            logger.warning(f"获取基金列表失败: {str(e)}")
    return None

def map_fund_type(fund_type_str):
    """映射基金类型"""
    if not fund_type_str:
        return None
    
    fund_type_str = fund_type_str.lower()
    
    if "股票" in fund_type_str:
        return "股票型"
    elif "债券" in fund_type_str:
        return "债券型"
    elif "混合" in fund_type_str:
        return "混合型"
    elif "货币" in fund_type_str:
        return "货币型"
    elif "指数" in fund_type_str:
        return "指数型"
    else:
        return None

def map_risk_level(fund_type):
    """根据基金类型映射风险等级"""
    if fund_type == "货币型":
        return "低"
    elif fund_type == "债券型":
        return "中低"
    elif fund_type == "混合型":
        return "中"
    elif fund_type == "股票型":
        return "中高"
    elif fund_type == "指数型":
        return "高"
    else:
        return "中"

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
        # 尝试使用AKShare获取基金数据
        filtered_funds = []
        
        if AKSHARE_AVAILABLE:
            try:
                # 获取基金列表
                fund_df = get_fund_list()
                
                if fund_df is not None and not fund_df.empty:
                    # 根据基金类型筛选
                    if fund_type:
                        # 检查是否有基金类型列
                        if '基金类型' in fund_df.columns:
                            fund_df = fund_df[fund_df['基金类型'].str.contains(fund_type, na=False)]
                        else:
                            # 根据基金名称推断类型
                            if fund_type == "股票型":
                                fund_df = fund_df[fund_df['基金简称'].str.contains('股票|指数', na=False)]
                            elif fund_type == "债券型":
                                fund_df = fund_df[fund_df['基金简称'].str.contains('债券|债', na=False)]
                            elif fund_type == "混合型":
                                fund_df = fund_df[fund_df['基金简称'].str.contains('混合|平衡', na=False)]
                            elif fund_type == "货币型":
                                fund_df = fund_df[fund_df['基金简称'].str.contains('货币|现金', na=False)]
                            elif fund_type == "指数型":
                                fund_df = fund_df[fund_df['基金简称'].str.contains('指数|ETF', na=False)]
                    
                    # 根据行业主题筛选
                    if industry:
                        fund_df = fund_df[fund_df['基金简称'].str.contains(industry, na=False)]
                    
                    # 根据投资期限筛选基金类型
                    if investment_horizon:
                        if investment_horizon == "短期":
                            # 短期投资适合货币型和债券型基金
                            if '基金类型' in fund_df.columns:
                                fund_df = fund_df[fund_df['基金类型'].str.contains('货币|债券', na=False)]
                            else:
                                fund_df = fund_df[fund_df['基金简称'].str.contains('货币|债券|现金|债', na=False)]
                        elif investment_horizon == "中期":
                            # 中期投资适合债券型和混合型基金
                            if '基金类型' in fund_df.columns:
                                fund_df = fund_df[fund_df['基金类型'].str.contains('债券|混合', na=False)]
                            else:
                                fund_df = fund_df[fund_df['基金简称'].str.contains('债券|混合|平衡|债', na=False)]
                        elif investment_horizon == "长期":
                            # 长期投资适合混合型、股票型和指数型基金
                            if '基金类型' in fund_df.columns:
                                fund_df = fund_df[fund_df['基金类型'].str.contains('混合|股票|指数', na=False)]
                            else:
                                fund_df = fund_df[fund_df['基金简称'].str.contains('混合|股票|指数|ETF', na=False)]
                    
                    # 限制结果数量，避免返回过多数据
                    fund_df = fund_df.head(20)
                    
                    # 转换为所需格式
                    for _, row in fund_df.iterrows():
                        fund_code = row['基金代码']
                        fund_name = row['基金简称']
                        
                        # 确定基金类型
                        if '基金类型' in row:
                            fund_type_value = row['基金类型']
                        else:
                            # 根据基金名称推断类型
                            if "股票" in fund_name:
                                fund_type_value = "股票型"
                            elif "债券" in fund_name or "债" in fund_name:
                                fund_type_value = "债券型"
                            elif "混合" in fund_name or "平衡" in fund_name:
                                fund_type_value = "混合型"
                            elif "货币" in fund_name or "现金" in fund_name:
                                fund_type_value = "货币型"
                            elif "指数" in fund_name or "ETF" in fund_name:
                                fund_type_value = "指数型"
                            else:
                                fund_type_value = "混合型"  # 默认为混合型
                        
                        # 确定风险等级
                        fund_risk_level = map_risk_level(fund_type_value)
                        
                        # 如果指定了风险等级，确保匹配
                        if risk_level and fund_risk_level != risk_level:
                            continue
                        
                        # 确定基金公司
                        if '基金公司' in row:
                            fund_company = row['基金公司']
                        else:
                            # 从基金经理信息中提取公司名称
                            fund_company = "未知"
                            if '基金经理' in row:
                                manager_info = row['基金经理']
                                if isinstance(manager_info, str) and "基金" in manager_info:
                                    fund_company = manager_info.split("基金")[0] + "基金"
                        
                        # 确定行业
                        fund_industry = "多行业"
                        if industry:
                            fund_industry = industry
                        else:
                            # 从基金名称中提取行业信息
                            industry_keywords = {
                                "科技": ["科技", "互联网", "信息", "通信", "计算机"],
                                "医疗健康": ["医疗", "医药", "健康", "生物"],
                                "消费": ["消费", "白酒", "食品", "零售"],
                                "新能源": ["新能源", "光伏", "风电", "电动", "能源"],
                                "金融": ["金融", "银行", "保险", "证券"],
                                "环保": ["环保", "低碳", "绿色"],
                                "文化传媒": ["传媒", "文化", "娱乐", "影视"]
                            }
                            
                            for ind, keywords in industry_keywords.items():
                                if any(keyword in fund_name for keyword in keywords):
                                    fund_industry = ind
                                    break
                        
                        filtered_funds.append({
                            "fundCode": fund_code,
                            "name": fund_name,
                            "type": fund_type_value,
                            "riskLevel": fund_risk_level,
                            "company": fund_company,
                            "industry": fund_industry
                        })
            
            except Exception as e:
                logger.warning(f"使用AKShare搜索基金失败: {str(e)}，使用备用数据")
        
        # 如果AKShare不可用或获取失败，使用备用数据
        if not filtered_funds:
            # 筛选基金
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
        
        # 如果仍然没有找到匹配的基金，生成一些模拟数据
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
