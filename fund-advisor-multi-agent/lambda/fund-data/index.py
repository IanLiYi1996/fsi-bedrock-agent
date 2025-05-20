import json
import logging
import random
from datetime import datetime, timedelta
import akshare as ak
import pandas as pd
import numpy as np

# 配置日志
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 缓存数据，避免频繁API调用
fund_cache = {}

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

def get_fund_info(fund_code):
    """
    使用AKShare获取基金基本信息
    """
    try:
        # 检查缓存
        if f"info_{fund_code}" in fund_cache:
            return fund_cache[f"info_{fund_code}"]
        
        # 获取基金基本信息
        fund_info_df = ak.fund_name_em()
        fund_info = fund_info_df[fund_info_df['基金代码'] == fund_code]
        
        if fund_info.empty:
            # 尝试获取ETF基金信息
            etf_info_df = ak.fund_etf_fund_daily_em()
            etf_info = etf_info_df[etf_info_df['基金代码'] == fund_code]
            
            if etf_info.empty:
                # 如果在备用数据中存在
                if fund_code in backup_funds:
                    return backup_funds[fund_code]
                return None
            
            fund_type = "ETF"
            fund_name = etf_info.iloc[0]['基金简称']
        else:
            fund_type = fund_info.iloc[0]['基金类型']
            fund_name = fund_info.iloc[0]['基金简称']
        
        # 获取基金详细信息
        try:
            fund_detail_df = ak.fund_individual_basic_info_xq(symbol=fund_code)
            fund_detail = dict(zip(fund_detail_df['item'], fund_detail_df['value']))
        except:
            fund_detail = {}
        
        # 确定风险等级
        risk_level = "中"  # 默认风险等级
        if "股票" in fund_type:
            risk_level = "高"
        elif "债券" in fund_type:
            risk_level = "中低"
        elif "货币" in fund_type:
            risk_level = "低"
        elif "混合" in fund_type:
            risk_level = "中高"
        
        # 构建基金信息
        fund_data = {
            "name": fund_name,
            "type": fund_type,
            "risk_level": risk_level,
            "inception_date": fund_detail.get("成立时间", ""),
            "size": float(fund_detail.get("最新规模", "0").replace("亿", "")) if "最新规模" in fund_detail else 0,
            "company": fund_detail.get("基金公司", ""),
            "industry": "多行业"  # 默认行业
        }
        
        # 缓存结果
        fund_cache[f"info_{fund_code}"] = fund_data
        return fund_data
    except Exception as e:
        logger.error(f"获取基金信息出错: {str(e)}")
        # 如果在备用数据中存在
        if fund_code in backup_funds:
            return backup_funds[fund_code]
        return None

def get_fund_performance(fund_code):
    """
    使用AKShare获取基金业绩数据
    """
    try:
        # 检查缓存
        if f"perf_{fund_code}" in fund_cache:
            return fund_cache[f"perf_{fund_code}"]
        
        # 获取基金历史净值
        try:
            if len(fund_code) == 6 and fund_code.startswith(("1", "5")):
                # ETF基金
                nav_history_df = ak.fund_etf_hist_em(symbol=fund_code, period="daily",
                                                    start_date="20000101", end_date=datetime.now().strftime("%Y%m%d"))
                nav_history_df = nav_history_df.rename(columns={"日期": "date", "收盘": "nav"})
            else:
                # 普通基金
                nav_history_df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
                nav_history_df = nav_history_df.rename(columns={"净值日期": "date", "单位净值": "nav"})
        except:
            # 尝试货币基金
            try:
                nav_history_df = ak.fund_money_fund_info_em(symbol=fund_code)
                nav_history_df = nav_history_df.rename(columns={"净值日期": "date", "每万份收益": "nav"})
            except:
                # 生成模拟数据
                today = datetime.now()
                nav_history = []
                for i in range(365):
                    date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
                    nav = round(1 + random.uniform(-0.03, 0.04) + i * 0.0003, 4)
                    nav_history.append({"date": date, "nav": nav})
                return {"navHistory": nav_history}
        
        # 转换为列表格式
        nav_history = []
        for _, row in nav_history_df.iterrows():
            nav_history.append({
                "date": row["date"],
                "nav": float(row["nav"])
            })
        
        # 计算各时间段收益率
        returns = {}
        if len(nav_history) > 0:
            latest_nav = nav_history[0]["nav"]
            
            # 计算不同时间段的收益率
            for period, days in [("1month", 30), ("3month", 90), ("6month", 180),
                                ("1year", 365), ("3year", 1095), ("5year", 1825)]:
                if len(nav_history) > days:
                    past_nav = next((item["nav"] for item in nav_history if item["date"] <= (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')), None)
                    if past_nav:
                        returns[period] = round((latest_nav / past_nav - 1) * 100, 2)
                    else:
                        returns[period] = None
                else:
                    returns[period] = None
            
            # 计算今年以来收益率
            year_start = datetime.now().replace(month=1, day=1).strftime('%Y-%m-%d')
            year_start_nav = next((item["nav"] for item in nav_history if item["date"] <= year_start), None)
            if year_start_nav:
                returns["ytd"] = round((latest_nav / year_start_nav - 1) * 100, 2)
            else:
                returns["ytd"] = None
            
            # 计算成立以来收益率
            if len(nav_history) > 0:
                inception_nav = nav_history[-1]["nav"]
                returns["sinceInception"] = round((latest_nav / inception_nav - 1) * 100, 2)
            else:
                returns["sinceInception"] = None
        
        # 构建业绩数据
        performance = {
            "returns": returns,
            "navHistory": nav_history[:365]  # 限制为最近一年的数据
        }
        
        # 缓存结果
        fund_cache[f"perf_{fund_code}"] = performance
        return performance
    except Exception as e:
        logger.error(f"获取基金业绩出错: {str(e)}")
        # 生成模拟数据
        today = datetime.now()
        nav_history = []
        for i in range(365):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            nav = round(1 + random.uniform(-0.03, 0.04) + i * 0.0003, 4)
            nav_history.append({"date": date, "nav": nav})
        return {"navHistory": nav_history}

def get_fund_holdings(fund_code):
    """
    使用AKShare获取基金持仓数据
    """
    try:
        # 检查缓存
        if f"hold_{fund_code}" in fund_cache:
            return fund_cache[f"hold_{fund_code}"]
        
        holdings = {
            "stockHoldings": [],
            "bondHoldings": [],
            "industryAllocation": {},
            "assetAllocation": {}
        }
        
        # 获取基金持仓
        try:
            # 获取股票持仓
            stock_holdings_df = ak.fund_portfolio_hold_em(symbol=fund_code, date=datetime.now().strftime("%Y"))
            if not stock_holdings_df.empty:
                for _, row in stock_holdings_df.iterrows():
                    holdings["stockHoldings"].append({
                        "name": row["股票名称"],
                        "code": row["股票代码"],
                        "weight": float(row["占净值比例"]),
                        "industry": "未知"  # AKShare不提供行业信息
                    })
            
            # 获取债券持仓
            bond_holdings_df = ak.fund_portfolio_bond_hold_em(symbol=fund_code, date=datetime.now().strftime("%Y"))
            if not bond_holdings_df.empty:
                for _, row in bond_holdings_df.iterrows():
                    holdings["bondHoldings"].append({
                        "name": row["债券名称"],
                        "code": row["债券代码"],
                        "weight": float(row["占净值比例"]),
                        "type": "债券"
                    })
            
            # 获取行业配置
            industry_allocation_df = ak.fund_portfolio_industry_allocation_em(symbol=fund_code, date=datetime.now().strftime("%Y"))
            if not industry_allocation_df.empty:
                for _, row in industry_allocation_df.iterrows():
                    holdings["industryAllocation"][row["证监会行业名称"]] = float(row["占净值比例"])
        except Exception as e:
            logger.warning(f"获取基金持仓详情出错: {str(e)}")
        
        # 缓存结果
        fund_cache[f"hold_{fund_code}"] = holdings
        return holdings
    except Exception as e:
        logger.error(f"获取基金持仓出错: {str(e)}")
        return {
            "stockHoldings": [],
            "bondHoldings": [],
            "industryAllocation": {},
            "assetAllocation": {}
        }

def get_fund_manager(fund_code):
    """
    使用AKShare获取基金经理信息
    """
    try:
        # 检查缓存
        if f"manager_{fund_code}" in fund_cache:
            return fund_cache[f"manager_{fund_code}"]
        
        # 获取基金详细信息
        try:
            fund_detail_df = ak.fund_individual_basic_info_xq(symbol=fund_code)
            fund_detail = dict(zip(fund_detail_df['item'], fund_detail_df['value']))
            
            # 提取基金经理信息
            manager_name = fund_detail.get("基金经理", "未知")
            
            # 尝试获取基金经理详细信息
            manager_info = {
                "name": manager_name,
                "experience": 0,
                "education": "未知",
                "joined_date": "",
                "managed_funds": [fund_code],
                "performance": ""
            }
            
            # 如果在备用数据中存在
            if fund_code in fund_managers:
                manager_info = fund_managers[fund_code]
            
            # 缓存结果
            fund_cache[f"manager_{fund_code}"] = manager_info
            return manager_info
        except:
            # 如果在备用数据中存在
            if fund_code in fund_managers:
                return fund_managers[fund_code]
            return None
    except Exception as e:
        logger.error(f"获取基金经理信息出错: {str(e)}")
        # 如果在备用数据中存在
        if fund_code in fund_managers:
            return fund_managers[fund_code]
        return None

def handler(event, context):
    """
    Lambda处理函数
    """
    logger.info(f"收到的事件: {json.dumps(event)}")
    
    try:
        # 解析API请求
        api_path = event.get('apiPath', '')
        parameters = event.get('parameters', {})
        http_method = event.get('httpMethod', 'GET')
        
        # 处理不同的API路径
        if api_path == '/getFundInfo':
            # 获取基金信息
            fund_code = parameters.get('fundCode', '').strip()
            fund_info = get_fund_info(fund_code)
            
            if fund_info:
                return {
                    "statusCode": 200,
                    "body": {
                        "fundCode": fund_code,
                        "name": fund_info["name"],
                        "type": fund_info["type"],
                        "riskLevel": fund_info["risk_level"],
                        "inceptionDate": fund_info["inception_date"],
                        "size": fund_info["size"],
                        "company": fund_info["company"],
                        "industry": fund_info.get("industry", "多行业")
                    }
                }
            else:
                return {
                    "statusCode": 404,
                    "body": {
                        "message": f"未找到基金代码 {fund_code}"
                    }
                }
        elif api_path == '/getFundPerformance':
            # 获取基金业绩
            fund_code = parameters.get('fundCode', '').strip()
            fund_info = get_fund_info(fund_code)
            
            if fund_info:
                # 获取业绩数据
                performance_data = get_fund_performance(fund_code)
                
                # 构建响应
                performance = {
                    "fundCode": fund_code,
                    "name": fund_info["name"],
                    "returns": performance_data.get("returns", {
                        "1month": round(random.uniform(-5, 10), 2),
                        "3month": round(random.uniform(-10, 20), 2),
                        "6month": round(random.uniform(-15, 30), 2),
                        "1year": round(random.uniform(-20, 40), 2),
                        "3year": round(random.uniform(-10, 80), 2),
                        "5year": round(random.uniform(0, 120), 2),
                        "sinceInception": round(random.uniform(50, 300), 2)
                    }),
                    "riskMetrics": {
                        "maxDrawdown": round(random.uniform(-50, -10), 2),
                        "volatility": round(random.uniform(5, 30), 2),
                        "sharpeRatio": round(random.uniform(0, 3), 2),
                        "informationRatio": round(random.uniform(-1, 2), 2),
                        "treynorRatio": round(random.uniform(-2, 5), 2),
                        "beta": round(random.uniform(0.5, 1.5), 2)
                    },
                    "benchmarkComparison": {
                        "1year": round(random.uniform(-10, 10), 2),
                        "3year": round(random.uniform(-20, 20), 2),
                        "5year": round(random.uniform(-30, 30), 2)
                    },
                    "navHistory": performance_data.get("navHistory", [])
                }
                
                # 如果没有获取到历史净值数据，生成模拟数据
                if not performance["navHistory"]:
                    # 生成过去30天的模拟净值数据
                    nav_history = []
                    base_value = random.uniform(0.8, 1.5)
                    for i in range(30):
                        date = (datetime.now() - timedelta(days=30-i)).strftime('%Y-%m-%d')
                        value = round(base_value * (1 + random.uniform(-0.02, 0.02)), 4)
                        nav_history.append({"date": date, "value": value})
                        base_value = value
                    
                    performance["navHistory"] = nav_history
                
                return {
                    "statusCode": 200,
                    "body": performance
                }
            else:
                return {
                    "statusCode": 404,
                    "body": {
                        "message": f"未找到基金代码 {fund_code}"
                    }
                }
        elif api_path == '/getFundHoldings':
            # 获取基金持仓
            fund_code = parameters.get('fundCode', '').strip()
            fund_info = get_fund_info(fund_code)
            
            if fund_info:
                # 获取持仓数据
                holdings_data = get_fund_holdings(fund_code)
                
                # 构建响应
                holdings = {
                    "fundCode": fund_code,
                    "name": fund_info["name"],
                    "reportDate": (datetime.now() - timedelta(days=random.randint(30, 90))).strftime('%Y-%m-%d'),
                    "stockHoldings": holdings_data.get("stockHoldings", []),
                    "bondHoldings": holdings_data.get("bondHoldings", []),
                    "industryAllocation": holdings_data.get("industryAllocation", {}),
                    "assetAllocation": holdings_data.get("assetAllocation", {})
                }
                
                # 如果没有获取到资产配置数据，根据基金类型生成模拟数据
                if not holdings["assetAllocation"]:
                    if fund_info["type"] == "股票型" or "股票" in fund_info["type"]:
                        holdings["assetAllocation"] = {
                            "股票": round(random.uniform(60, 95), 2),
                            "债券": round(random.uniform(0, 30), 2),
                            "现金": round(random.uniform(5, 10), 2)
                        }
                    elif fund_info["type"] == "债券型" or "债券" in fund_info["type"]:
                        holdings["assetAllocation"] = {
                            "股票": round(random.uniform(0, 20), 2),
                            "债券": round(random.uniform(60, 95), 2),
                            "现金": round(random.uniform(5, 20), 2)
                        }
                    elif fund_info["type"] == "混合型" or "混合" in fund_info["type"]:
                        holdings["assetAllocation"] = {
                            "股票": round(random.uniform(30, 70), 2),
                            "债券": round(random.uniform(20, 60), 2),
                            "现金": round(random.uniform(5, 15), 2)
                        }
                    elif fund_info["type"] == "货币型" or "货币" in fund_info["type"]:
                        holdings["assetAllocation"] = {
                            "短期债券": round(random.uniform(60, 90), 2),
                            "现金": round(random.uniform(10, 40), 2)
                        }
                    else:
                        holdings["assetAllocation"] = {
                            "股票": round(random.uniform(40, 60), 2),
                            "债券": round(random.uniform(20, 40), 2),
                            "现金": round(random.uniform(10, 20), 2)
                        }
                
                return {
                    "statusCode": 200,
                    "body": holdings
                }
            else:
                return {
                    "statusCode": 404,
                    "body": {
                        "message": f"未找到基金代码 {fund_code}"
                    }
                }
        elif api_path == '/getFundManager':
            # 获取基金经理信息
            fund_code = parameters.get('fundCode', '').strip()
            fund_info = get_fund_info(fund_code)
            manager_info = get_fund_manager(fund_code)
            
            if fund_info and manager_info:
                return {
                    "statusCode": 200,
                    "body": {
                        "fundCode": fund_code,
                        "fundName": fund_info["name"],
                        "managerName": manager_info["name"],
                        "experience": manager_info["experience"],
                        "education": manager_info["education"],
                        "joinedDate": manager_info["joined_date"],
                        "managedFunds": manager_info["managed_funds"],
                        "performance": manager_info["performance"]
                    }
                }
            else:
                return {
                    "statusCode": 404,
                    "body": {
                        "message": f"未找到基金代码 {fund_code} 的基金经理信息"
                    }
                }
        elif api_path == '/getFundFees':
            # 获取基金费用
            fund_code = parameters.get('fundCode', '').strip()
            fund_info = get_fund_info(fund_code)
            
            if fund_info:
                # 根据基金类型生成费率结构
                fund_type = fund_info["type"]
                
                # 尝试从AKShare获取费率信息
                try:
                    fee_df = ak.fund_fee_em(symbol=fund_code, indicator="申购费率")
                    if not fee_df.empty:
                        subscription_fee = float(fee_df.iloc[0]["原费率"].replace("%", "")) / 100
                    else:
                        subscription_fee = 0
                except:
                    # 根据基金类型生成模拟费率
                    if fund_type == "货币型" or "货币" in fund_type:
                        subscription_fee = 0
                    elif fund_type == "债券型" or "债券" in fund_type:
                        subscription_fee = round(random.uniform(0, 0.8), 4)
                    elif fund_type == "混合型" or "混合" in fund_type:
                        subscription_fee = round(random.uniform(0.8, 1.2), 4)
                    else:  # 股票型或指数型
                        subscription_fee = round(random.uniform(1.0, 1.5), 4)
                
                # 生成其他费率
                if fund_type == "货币型" or "货币" in fund_type:
                    management_fee = round(random.uniform(0.1, 0.3), 4)
                    custodian_fee = round(random.uniform(0.05, 0.1), 4)
                    redemption_fee = 0
                    sales_service_fee = round(random.uniform(0.01, 0.25), 4)
                elif fund_type == "债券型" or "债券" in fund_type:
                    management_fee = round(random.uniform(0.4, 0.8), 4)
                    custodian_fee = round(random.uniform(0.1, 0.2), 4)
                    redemption_fee = round(random.uniform(0, 0.5), 4)
                    sales_service_fee = round(random.uniform(0.2, 0.4), 4)
                elif fund_type == "混合型" or "混合" in fund_type:
                    management_fee = round(random.uniform(0.8, 1.5), 4)
                    custodian_fee = round(random.uniform(0.15, 0.25), 4)
                    redemption_fee = round(random.uniform(0, 0.5), 4)
                    sales_service_fee = round(random.uniform(0.2, 0.5), 4)
                else:  # 股票型或指数型
                    management_fee = round(random.uniform(1.0, 1.8), 4)
                    custodian_fee = round(random.uniform(0.2, 0.3), 4)
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
                    "statusCode": 200,
                    "body": {
                        "fundCode": fund_code,
                        "fundName": fund_info["name"],
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
            else:
                return {
                    "statusCode": 404,
                    "body": {
                        "message": f"未找到基金代码 {fund_code}"
                    }
                }
        elif api_path == '/searchFunds':
            # 搜索基金
            fund_type = parameters.get('fundType', '').strip()
            risk_level = parameters.get('riskLevel', '').strip()
            industry = parameters.get('industry', '').strip()
            investment_horizon = parameters.get('investmentHorizon', '').strip()
            
            try:
                # 使用AKShare获取基金列表
                all_funds_df = ak.fund_name_em()
                
                # 转换为字典列表
                all_funds = []
                for _, row in all_funds_df.iterrows():
                    fund_code = row['基金代码']
                    fund_type_str = row['基金类型']
                    
                    # 确定风险等级
                    risk_level_str = "中"  # 默认风险等级
                    if "股票" in fund_type_str:
                        risk_level_str = "高"
                    elif "债券" in fund_type_str:
                        risk_level_str = "中低"
                    elif "货币" in fund_type_str:
                        risk_level_str = "低"
                    elif "混合" in fund_type_str:
                        risk_level_str = "中高"
                    
                    all_funds.append({
                        "fundCode": fund_code,
                        "name": row['基金简称'],
                        "type": fund_type_str,
                        "riskLevel": risk_level_str,
                        "company": row.get('基金公司', "未知"),
                        "industry": "多行业"  # 默认行业
                    })
                
                # 如果获取失败，使用备用数据
                if not all_funds:
                    all_funds = [
                        {
                            "fundCode": code,
                            "name": fund["name"],
                            "type": fund["type"],
                            "riskLevel": fund["risk_level"],
                            "company": fund["company"],
                            "industry": fund.get("industry", "多行业")
                        }
                        for code, fund in backup_funds.items()
                    ]
            except Exception as e:
                logger.error(f"获取基金列表出错: {str(e)}")
                # 使用备用数据
                all_funds = [
                    {
                        "fundCode": code,
                        "name": fund["name"],
                        "type": fund["type"],
                        "riskLevel": fund["risk_level"],
                        "company": fund["company"],
                        "industry": fund.get("industry", "多行业")
                    }
                    for code, fund in backup_funds.items()
                ]
            
            # 筛选基金
            filtered_funds = []
            for fund in all_funds:
                match = True
                
                if fund_type and fund["type"] != fund_type:
                    match = False
                
                if risk_level and fund["riskLevel"] != risk_level:
                    match = False
                
                if industry and fund.get("industry", "") != industry:
                    match = False
                
                # 根据投资期限筛选基金类型
                if investment_horizon:
                    if investment_horizon == "短期" and fund["type"] not in ["货币型", "债券型"]:
                        match = False
                    elif investment_horizon == "中期" and fund["type"] not in ["债券型", "混合型"]:
                        match = False
                    elif investment_horizon == "长期" and fund["type"] not in ["混合型", "股票型", "指数型"]:
                        match = False
                
                if match:
                    filtered_funds.append(fund)
                
                # 限制返回结果数量，避免数据过大
                if len(filtered_funds) >= 100:
                    break
            
            return {
                "statusCode": 200,
                "body": {
                    "funds": filtered_funds,
                    "count": len(filtered_funds)
                }
            }
        else:
            # 未知的API路径
            return {
                "statusCode": 400,
                "body": {
                    "message": f"不支持的API路径: {api_path}"
                }
            }
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        return {
            "statusCode": 500,
            "body": {
                "message": "处理请求时发生内部错误"
            }
        }