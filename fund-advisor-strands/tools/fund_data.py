from strands import tool
import requests
import json
import os
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# 备用模拟基金数据（当API调用失败时使用）
backup_funds = {
    "000001": {
        "name": "华夏成长混合", 
        "type": "混合型", 
        "risk_level": "中高",
        "inception_date": "2001-12-18",
        "size": 56.78,  # 单位：亿元
        "company": "华夏基金"
    },
    "110022": {
        "name": "易方达消费行业股票", 
        "type": "股票型", 
        "risk_level": "高",
        "inception_date": "2010-08-20",
        "size": 123.45,
        "company": "易方达基金"
    },
    "000961": {
        "name": "天弘沪深300指数", 
        "type": "指数型", 
        "risk_level": "中高",
        "inception_date": "2015-03-31",
        "size": 89.12,
        "company": "天弘基金"
    },
    "000198": {
        "name": "中银纯债债券A", 
        "type": "债券型", 
        "risk_level": "中低",
        "inception_date": "2012-12-12",
        "size": 45.67,
        "company": "中银基金"
    },
    "000617": {
        "name": "易方达货币市场基金A", 
        "type": "货币型", 
        "risk_level": "低",
        "inception_date": "2005-02-02",
        "size": 234.56,
        "company": "易方达基金"
    },
    "001156": {
        "name": "申万菱信新能源汽车主题灵活配置混合", 
        "type": "混合型", 
        "risk_level": "中高",
        "inception_date": "2015-05-07",
        "size": 67.89,
        "company": "申万菱信基金",
        "industry": "新能源汽车"
    },
    "001975": {
        "name": "景顺长城环保优势股票", 
        "type": "股票型", 
        "risk_level": "高",
        "inception_date": "2016-03-15",
        "size": 34.56,
        "company": "景顺长城基金",
        "industry": "环保"
    },
    "003096": {
        "name": "中欧医疗健康混合A", 
        "type": "混合型", 
        "risk_level": "中高",
        "inception_date": "2016-09-29",
        "size": 78.90,
        "company": "中欧基金",
        "industry": "医疗健康"
    },
    "005827": {
        "name": "易方达蓝筹精选混合", 
        "type": "混合型", 
        "risk_level": "中高",
        "inception_date": "2018-09-05",
        "size": 56.78,
        "company": "易方达基金"
    },
    "001714": {
        "name": "工银瑞信文体产业股票A", 
        "type": "股票型", 
        "risk_level": "高",
        "inception_date": "2016-08-01",
        "size": 23.45,
        "company": "工银瑞信基金",
        "industry": "文化传媒"
    }
}

# 基金经理数据
fund_managers = {
    "000001": {
        "name": "王亚伟",
        "experience": 15,
        "education": "清华大学金融学硕士",
        "joined_date": "2005-06-01",
        "managed_funds": ["000001", "000123", "000456"],
        "performance": "王亚伟先生曾获得多次金牛基金经理奖项，擅长成长股投资，历史年化收益率约15%。"
    },
    "110022": {
        "name": "张坤",
        "experience": 12,
        "education": "北京大学经济学博士",
        "joined_date": "2008-05-15",
        "managed_funds": ["110022", "110033", "110044"],
        "performance": "张坤先生专注于消费行业研究，历史年化收益率约18%，曾获得金牛基金经理等奖项。"
    },
    "000961": {
        "name": "李雪松",
        "experience": 8,
        "education": "上海交通大学金融学硕士",
        "joined_date": "2012-03-20",
        "managed_funds": ["000961", "000962"],
        "performance": "李雪松先生专注于指数投资研究，追求稳定的指数跟踪效果，跟踪误差控制良好。"
    },
    "000198": {
        "name": "陈凯杨",
        "experience": 10,
        "education": "中国人民大学金融学硕士",
        "joined_date": "2010-07-01",
        "managed_funds": ["000198", "000199"],
        "performance": "陈凯杨先生擅长债券投资，注重信用风险控制，历史年化收益率约6%。"
    },
    "000617": {
        "name": "刘朝阳",
        "experience": 14,
        "education": "复旦大学经济学硕士",
        "joined_date": "2006-09-01",
        "managed_funds": ["000617", "000618"],
        "performance": "刘朝阳先生专注于货币市场研究，注重流动性管理和风险控制，历史年化收益率约3.5%。"
    },
    "001156": {
        "name": "李博",
        "experience": 9,
        "education": "中国科学院计算机博士",
        "joined_date": "2011-04-15",
        "managed_funds": ["001156", "001157"],
        "performance": "李博先生专注于新能源汽车产业链研究，历史年化收益率约16%。"
    },
    "001975": {
        "name": "杨锐文",
        "experience": 11,
        "education": "中山大学环境科学硕士",
        "joined_date": "2009-08-10",
        "managed_funds": ["001975", "001976"],
        "performance": "杨锐文先生专注于环保产业研究，历史年化收益率约14%。"
    },
    "003096": {
        "name": "葛兰",
        "experience": 10,
        "education": "北京协和医学院医学博士",
        "joined_date": "2010-06-01",
        "managed_funds": ["003096", "003097"],
        "performance": "葛兰女士拥有医学背景，专注于医疗健康行业研究，历史年化收益率约20%。"
    },
    "005827": {
        "name": "冯波",
        "experience": 13,
        "education": "上海财经大学金融学硕士",
        "joined_date": "2007-03-01",
        "managed_funds": ["005827", "005828"],
        "performance": "冯波先生擅长价值投资，专注于蓝筹股研究，历史年化收益率约12%。"
    },
    "001714": {
        "name": "郝兵",
        "experience": 8,
        "education": "中国传媒大学传媒经济学硕士",
        "joined_date": "2012-05-01",
        "managed_funds": ["001714", "001715"],
        "performance": "郝兵先生专注于文化传媒产业研究，历史年化收益率约15%。"
    }
}

@tool
def get_fund_info(fund_code: str) -> Dict[str, Any]:
    """
    获取基金基本信息
    
    Args:
        fund_code: 基金代码
    """
    try:
        # 实际实现可以调用外部API
        # 这里使用备用数据模拟
        if fund_code in backup_funds:
            return {
                "status": "success",
                "content": [
                    {
                        "json": {
                            "fundCode": fund_code,
                            "name": backup_funds[fund_code]["name"],
                            "type": backup_funds[fund_code]["type"],
                            "riskLevel": backup_funds[fund_code]["risk_level"],
                            "inceptionDate": backup_funds[fund_code]["inception_date"],
                            "size": backup_funds[fund_code]["size"],
                            "company": backup_funds[fund_code]["company"],
                            "industry": backup_funds[fund_code].get("industry", "多行业")
                        }
                    }
                ]
            }
        else:
            return {
                "status": "error",
                "content": [
                    {"text": f"未找到基金代码 {fund_code}"}
                ]
            }
    except Exception as e:
        return {
            "status": "error",
            "content": [
                {"text": f"获取基金信息出错: {str(e)}"}
            ]
        }

@tool
def get_fund_performance(fund_code: str) -> Dict[str, Any]:
    """
    获取基金业绩数据
    
    Args:
        fund_code: 基金代码
    """
    try:
        # 检查基金是否存在
        if fund_code not in backup_funds:
            return {
                "status": "error",
                "content": [
                    {"text": f"未找到基金代码 {fund_code}"}
                ]
            }
        
        # 生成模拟业绩数据
        returns = {
            "1month": round(random.uniform(-5, 10), 2),
            "3month": round(random.uniform(-10, 20), 2),
            "6month": round(random.uniform(-15, 30), 2),
            "1year": round(random.uniform(-20, 40), 2),
            "3year": round(random.uniform(-10, 80), 2),
            "5year": round(random.uniform(0, 120), 2),
            "sinceInception": round(random.uniform(50, 300), 2)
        }
        
        # 生成风险指标
        risk_metrics = {
            "maxDrawdown": round(random.uniform(-50, -10), 2),
            "volatility": round(random.uniform(5, 30), 2),
            "sharpeRatio": round(random.uniform(0, 3), 2),
            "informationRatio": round(random.uniform(-1, 2), 2),
            "treynorRatio": round(random.uniform(-2, 5), 2),
            "beta": round(random.uniform(0.5, 1.5), 2)
        }
        
        # 生成基准比较
        benchmark_comparison = {
            "1year": round(random.uniform(-10, 10), 2),
            "3year": round(random.uniform(-20, 20), 2),
            "5year": round(random.uniform(-30, 30), 2)
        }
        
        # 生成历史净值数据
        nav_history = []
        base_value = random.uniform(0.8, 1.5)
        today = datetime.now()
        for i in range(365):
            date = (today - timedelta(days=365-i)).strftime('%Y-%m-%d')
            value = round(base_value * (1 + random.uniform(-0.02, 0.02)), 4)
            nav_history.append({"date": date, "value": value})
            base_value = value
        
        return {
            "status": "success",
            "content": [
                {
                    "json": {
                        "fundCode": fund_code,
                        "name": backup_funds[fund_code]["name"],
                        "returns": returns,
                        "riskMetrics": risk_metrics,
                        "benchmarkComparison": benchmark_comparison,
                        "navHistory": nav_history
                    }
                }
            ]
        }
    except Exception as e:
        return {
            "status": "error",
            "content": [
                {"text": f"获取基金业绩数据出错: {str(e)}"}
            ]
        }

@tool
def get_fund_holdings(fund_code: str) -> Dict[str, Any]:
    """
    获取基金持仓数据
    
    Args:
        fund_code: 基金代码
    """
    try:
        # 检查基金是否存在
        if fund_code not in backup_funds:
            return {
                "status": "error",
                "content": [
                    {"text": f"未找到基金代码 {fund_code}"}
                ]
            }
        
        fund_type = backup_funds[fund_code]["type"]
        
        # 生成模拟股票持仓
        stock_holdings = []
        if "股票" in fund_type or "混合" in fund_type or "指数" in fund_type:
            stock_names = ["贵州茅台", "五粮液", "腾讯控股", "阿里巴巴", "中国平安", 
                          "招商银行", "格力电器", "美的集团", "恒瑞医药", "宁德时代"]
            stock_codes = ["600519", "000858", "00700", "09988", "601318", 
                          "600036", "000651", "000333", "600276", "300750"]
            industries = ["食品饮料", "食品饮料", "互联网", "互联网", "金融保险", 
                         "银行", "家电", "家电", "医药", "新能源"]
            
            total_weight = 0
            for i in range(min(10, len(stock_names))):
                weight = round(random.uniform(1, 10), 2)
                total_weight += weight
                stock_holdings.append({
                    "name": stock_names[i],
                    "code": stock_codes[i],
                    "weight": weight,
                    "industry": industries[i]
                })
            
            # 调整权重，使总和为合理值
            target_total = 70 if "股票" in fund_type else 50 if "混合" in fund_type else 90
            for holding in stock_holdings:
                holding["weight"] = round(holding["weight"] / total_weight * target_total, 2)
        
        # 生成模拟债券持仓
        bond_holdings = []
        if "债券" in fund_type or "混合" in fund_type:
            bond_names = ["21国债01", "21农发01", "21进出01", "21建设01", "21工商01"]
            bond_codes = ["210001", "210301", "210201", "210401", "210501"]
            
            total_weight = 0
            for i in range(min(5, len(bond_names))):
                weight = round(random.uniform(1, 10), 2)
                total_weight += weight
                bond_holdings.append({
                    "name": bond_names[i],
                    "code": bond_codes[i],
                    "weight": weight,
                    "type": "国债" if "国债" in bond_names[i] else "金融债"
                })
            
            # 调整权重，使总和为合理值
            target_total = 20 if "股票" in fund_type else 40 if "混合" in fund_type else 80
            for holding in bond_holdings:
                holding["weight"] = round(holding["weight"] / total_weight * target_total, 2)
        
        # 生成行业配置
        industry_allocation = {}
        if stock_holdings:
            industries = set(holding["industry"] for holding in stock_holdings)
            total_weight = 0
            for industry in industries:
                weight = round(random.uniform(5, 20), 2)
                total_weight += weight
                industry_allocation[industry] = weight
            
            # 调整权重，使总和为合理值
            target_total = 70 if "股票" in fund_type else 50 if "混合" in fund_type else 90
            for industry in industry_allocation:
                industry_allocation[industry] = round(industry_allocation[industry] / total_weight * target_total, 2)
        
        # 生成资产配置
        asset_allocation = {}
        if "股票" in fund_type:
            asset_allocation = {
                "股票": round(random.uniform(60, 95), 2),
                "债券": round(random.uniform(0, 30), 2),
                "现金": round(random.uniform(5, 10), 2)
            }
        elif "债券" in fund_type:
            asset_allocation = {
                "股票": round(random.uniform(0, 20), 2),
                "债券": round(random.uniform(60, 95), 2),
                "现金": round(random.uniform(5, 20), 2)
            }
        elif "混合" in fund_type:
            asset_allocation = {
                "股票": round(random.uniform(30, 70), 2),
                "债券": round(random.uniform(20, 60), 2),
                "现金": round(random.uniform(5, 15), 2)
            }
        elif "货币" in fund_type:
            asset_allocation = {
                "短期债券": round(random.uniform(60, 90), 2),
                "现金": round(random.uniform(10, 40), 2)
            }
        else:
            asset_allocation = {
                "股票": round(random.uniform(40, 60), 2),
                "债券": round(random.uniform(20, 40), 2),
                "现金": round(random.uniform(10, 20), 2)
            }
        
        # 确保资产配置总和为100%
        total = sum(asset_allocation.values())
        for asset in asset_allocation:
            asset_allocation[asset] = round(asset_allocation[asset] / total * 100, 2)
        
        return {
            "status": "success",
            "content": [
                {
                    "json": {
                        "fundCode": fund_code,
                        "name": backup_funds[fund_code]["name"],
                        "reportDate": (datetime.now() - timedelta(days=random.randint(30, 90))).strftime('%Y-%m-%d'),
                        "stockHoldings": stock_holdings,
                        "bondHoldings": bond_holdings,
                        "industryAllocation": industry_allocation,
                        "assetAllocation": asset_allocation
                    }
                }
            ]
        }
    except Exception as e:
        return {
            "status": "error",
            "content": [
                {"text": f"获取基金持仓数据出错: {str(e)}"}
            ]
        }

@tool
def get_fund_manager(fund_code: str) -> Dict[str, Any]:
    """
    获取基金经理信息
    
    Args:
        fund_code: 基金代码
    """
    try:
        # 检查基金是否存在
        if fund_code not in backup_funds:
            return {
                "status": "error",
                "content": [
                    {"text": f"未找到基金代码 {fund_code}"}
                ]
            }
        
        # 检查是否有基金经理信息
        if fund_code not in fund_managers:
            # 生成随机基金经理信息
            manager_names = ["王明", "李强", "张伟", "刘洋", "陈晓", "赵华", "周鑫"]
            educations = ["清华大学金融学硕士", "北京大学经济学博士", "上海交通大学金融学硕士", 
                         "中国人民大学金融学博士", "复旦大学经济学硕士"]
            
            manager_info = {
                "name": random.choice(manager_names),
                "experience": random.randint(5, 20),
                "education": random.choice(educations),
                "joined_date": f"20{random.randint(10, 20)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                "managed_funds": [fund_code],
                "performance": f"历史年化收益率约{random.randint(5, 20)}%。"
            }
        else:
            manager_info = fund_managers[fund_code]
        
        return {
            "status": "success",
            "content": [
                {
                    "json": {
                        "fundCode": fund_code,
                        "fundName": backup_funds[fund_code]["name"],
                        "managerName": manager_info["name"],
                        "experience": manager_info["experience"],
                        "education": manager_info["education"],
                        "joinedDate": manager_info["joined_date"],
                        "managedFunds": manager_info["managed_funds"],
                        "performance": manager_info["performance"]
                    }
                }
            ]
        }
    except Exception as e:
        return {
            "status": "error",
            "content": [
                {"text": f"获取基金经理信息出错: {str(e)}"}
            ]
        }

@tool
def get_fund_fees(fund_code: str) -> Dict[str, Any]:
    """
    获取基金费用结构
    
    Args:
        fund_code: 基金代码
    """
    try:
        # 检查基金是否存在
        if fund_code not in backup_funds:
            return {
                "status": "error",
                "content": [
                    {"text": f"未找到基金代码 {fund_code}"}
                ]
            }
        
        fund_type = backup_funds[fund_code]["type"]
        
        # 根据基金类型生成费率结构
        if fund_type == "货币型" or "货币" in fund_type:
            management_fee = round(random.uniform(0.1, 0.3), 4)
            custodian_fee = round(random.uniform(0.05, 0.1), 4)
            subscription_fee = 0
            redemption_fee = 0
            sales_service_fee = round(random.uniform(0.01, 0.25), 4)
        elif fund_type == "债券型" or "债券" in fund_type:
            management_fee = round(random.uniform(0.4, 0.8), 4)
            custodian_fee = round(random.uniform(0.1, 0.2), 4)
            subscription_fee = round(random.uniform(0, 0.8), 4)
            redemption_fee = round(random.uniform(0, 0.5), 4)
            sales_service_fee = round(random.uniform(0.2, 0.4), 4)
        elif fund_type == "混合型" or "混合" in fund_type:
            management_fee = round(random.uniform(0.8, 1.5), 4)
            custodian_fee = round(random.uniform(0.15, 0.25), 4)
            subscription_fee = round(random.uniform(0.8, 1.2), 4)
            redemption_fee = round(random.uniform(0, 0.5), 4)
            sales_service_fee = round(random.uniform(0.2, 0.5), 4)
        else:  # 股票型或指数型
            management_fee = round(random.uniform(1.0, 1.8), 4)
            custodian_fee = round(random.uniform(0.2, 0.3), 4)
            subscription_fee = round(random.uniform(1.0, 1.5), 4)
            redemption_fee = round(random.uniform(0, 0.5), 4)
            sales_service_fee = round(random.uniform(0.3, 0.6), 4)
        
        # 生成阶梯式申购费率
        subscription_fee_tiers = []
        if subscription_fee > 0:
            subscription_fee_tiers = [
                {"amount": "100万以下", "rate": subscription_fee},
                {"amount": "100万-500万", "rate": round(subscription_fee * 0.6, 4)},
                {"amount": "500万-1000万", "rate": round(subscription_fee * 0.3, 4)},
                {"amount": "1000万以上", "rate": round(subscription_fee * 0.1, 4)}
            ]
        
        # 生成阶梯式赎回费率
        redemption_fee_tiers = []
        if redemption_fee > 0:
            redemption_fee_tiers = [
                {"holdingPeriod": "7天以内", "rate": round(redemption_fee * 1.5, 4)},
                {"holdingPeriod": "7天-30天", "rate": redemption_fee},
                {"holdingPeriod": "30天-180天", "rate": round(redemption_fee * 0.5, 4)},
                {"holdingPeriod": "180天-365天", "rate": round(redemption_fee * 0.25, 4)},
                {"holdingPeriod": "365天以上", "rate": 0}
            ]
        
        return {
            "status": "success",
            "content": [
                {
                    "json": {
                        "fundCode": fund_code,
                        "fundName": backup_funds[fund_code]["name"],
                        "managementFee": management_fee,
                        "custodianFee": custodian_fee,
                        "subscriptionFee": subscription_fee,
                        "subscriptionFeeTiers": subscription_fee_tiers,
                        "redemptionFee": redemption_fee,
                        "redemptionFeeTiers": redemption_fee_tiers,
                        "salesServiceFee": sales_service_fee,
                        "totalExpenseRatio": round(management_fee + custodian_fee + sales_service_fee, 4)
                    }
                }
            ]
        }
    except Exception as e:
        return {
            "status": "error",
            "content": [
                {"text": f"获取基金费用结构出错: {str(e)}"}
            ]
        }
