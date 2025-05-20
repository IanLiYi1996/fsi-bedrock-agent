import json
import logging
import random
from datetime import datetime, timedelta

# 配置日志
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 模拟基金数据
funds = {
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
            if fund_code in funds:
                return {
                    "statusCode": 200,
                    "body": {
                        "fundCode": fund_code,
                        "name": funds[fund_code]["name"],
                        "type": funds[fund_code]["type"],
                        "riskLevel": funds[fund_code]["risk_level"],
                        "inceptionDate": funds[fund_code]["inception_date"],
                        "size": funds[fund_code]["size"],
                        "company": funds[fund_code]["company"],
                        "industry": funds[fund_code].get("industry", "多行业")
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
            if fund_code in funds:
                # 生成模拟业绩数据
                today = datetime.now()
                
                # 生成不同时间段的收益率
                performance = {
                    "fundCode": fund_code,
                    "name": funds[fund_code]["name"],
                    "returns": {
                        "1month": round(random.uniform(-5, 10), 2),
                        "3month": round(random.uniform(-10, 20), 2),
                        "6month": round(random.uniform(-15, 30), 2),
                        "1year": round(random.uniform(-20, 40), 2),
                        "3year": round(random.uniform(-10, 80), 2),
                        "5year": round(random.uniform(0, 120), 2),
                        "sinceInception": round(random.uniform(50, 300), 2)
                    },
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
                    }
                }
                
                # 生成历史净值数据
                nav_history = []
                for i in range(365):
                    date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
                    # 基于基金类型生成不同的净值波动
                    if funds[fund_code]["type"] == "货币型":
                        nav = round(1 + i * 0.0001, 4)
                    elif funds[fund_code]["type"] == "债券型":
                        nav = round(1 + random.uniform(-0.01, 0.02) + i * 0.0002, 4)
                    elif funds[fund_code]["type"] == "混合型":
                        nav = round(1 + random.uniform(-0.03, 0.04) + i * 0.0003, 4)
                    else:  # 股票型或指数型
                        nav = round(1 + random.uniform(-0.05, 0.06) + i * 0.0004, 4)
                    
                    nav_history.append({"date": date, "nav": nav})
                
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
            if fund_code in funds:
                # 生成模拟持仓数据
                holdings = {
                    "fundCode": fund_code,
                    "name": funds[fund_code]["name"],
                    "reportDate": (datetime.now() - timedelta(days=random.randint(30, 90))).strftime('%Y-%m-%d'),
                    "stockHoldings": [],
                    "bondHoldings": [],
                    "industryAllocation": {},
                    "assetAllocation": {}
                }
                
                # 根据基金类型生成不同的持仓结构
                if funds[fund_code]["type"] in ["股票型", "混合型", "指数型"]:
                    # 生成股票持仓
                    stock_industries = ["科技", "医疗健康", "消费", "金融", "能源", "制造业", "房地产", "通信", "公用事业", "原材料"]
                    stock_count = random.randint(30, 100)
                    industry_allocation = {}
                    
                    for i in range(stock_count):
                        industry = random.choice(stock_industries)
                        weight = round(random.uniform(0.1, 5.0), 2) if i >= 10 else round(random.uniform(2.0, 10.0), 2)
                        
                        # 更新行业配置
                        if industry in industry_allocation:
                            industry_allocation[industry] += weight
                        else:
                            industry_allocation[industry] = weight
                        
                        holdings["stockHoldings"].append({
                            "name": f"股票{i+1}",
                            "code": f"60{i:04d}",
                            "industry": industry,
                            "weight": weight,
                            "marketValue": round(funds[fund_code]["size"] * weight / 100 * 100000000, 2)  # 转换为元
                        })
                    
                    # 对持仓按权重排序
                    holdings["stockHoldings"] = sorted(holdings["stockHoldings"], key=lambda x: x["weight"], reverse=True)
                    
                    # 更新行业配置
                    holdings["industryAllocation"] = {k: round(v, 2) for k, v in industry_allocation.items()}
                    
                    # 资产配置
                    stock_ratio = round(random.uniform(60, 95), 2) if funds[fund_code]["type"] == "股票型" else round(random.uniform(30, 70), 2)
                    bond_ratio = round(random.uniform(0, 30), 2)
                    cash_ratio = round(100 - stock_ratio - bond_ratio, 2)
                    
                    holdings["assetAllocation"] = {
                        "股票": stock_ratio,
                        "债券": bond_ratio,
                        "现金": cash_ratio
                    }
                
                if funds[fund_code]["type"] in ["债券型", "混合型"]:
                    # 生成债券持仓
                    bond_types = ["国债", "金融债", "企业债", "可转债", "中期票据"]
                    bond_count = random.randint(10, 50)
                    
                    for i in range(bond_count):
                        bond_type = random.choice(bond_types)
                        weight = round(random.uniform(0.5, 5.0), 2)
                        
                        holdings["bondHoldings"].append({
                            "name": f"{bond_type}{i+1}",
                            "code": f"10{i:04d}",
                            "type": bond_type,
                            "weight": weight,
                            "marketValue": round(funds[fund_code]["size"] * weight / 100 * 100000000, 2),  # 转换为元
                            "duration": round(random.uniform(1, 10), 2),
                            "yield": round(random.uniform(2, 6), 2)
                        })
                    
                    # 对持仓按权重排序
                    holdings["bondHoldings"] = sorted(holdings["bondHoldings"], key=lambda x: x["weight"], reverse=True)
                    
                    # 如果是债券型基金，更新资产配置
                    if funds[fund_code]["type"] == "债券型":
                        stock_ratio = round(random.uniform(0, 20), 2)
                        bond_ratio = round(random.uniform(60, 95), 2)
                        cash_ratio = round(100 - stock_ratio - bond_ratio, 2)
                        
                        holdings["assetAllocation"] = {
                            "股票": stock_ratio,
                            "债券": bond_ratio,
                            "现金": cash_ratio
                        }
                
                if funds[fund_code]["type"] == "货币型":
                    # 货币基金主要持有短期债券和现金
                    holdings["assetAllocation"] = {
                        "短期债券": round(random.uniform(60, 90), 2),
                        "现金": round(random.uniform(10, 40), 2)
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
            if fund_code in funds and fund_code in fund_managers:
                manager = fund_managers[fund_code]
                return {
                    "statusCode": 200,
                    "body": {
                        "fundCode": fund_code,
                        "fundName": funds[fund_code]["name"],
                        "managerName": manager["name"],
                        "experience": manager["experience"],
                        "education": manager["education"],
                        "joinedDate": manager["joined_date"],
                        "managedFunds": manager["managed_funds"],
                        "performance": manager["performance"]
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
            if fund_code in funds:
                # 根据基金类型生成不同的费率结构
                fund_type = funds[fund_code]["type"]
                
                if fund_type == "货币型":
                    management_fee = round(random.uniform(0.1, 0.3), 4)
                    custodian_fee = round(random.uniform(0.05, 0.1), 4)
                    subscription_fee = 0
                    redemption_fee = 0
                    sales_service_fee = round(random.uniform(0.01, 0.25), 4)
                elif fund_type == "债券型":
                    management_fee = round(random.uniform(0.4, 0.8), 4)
                    custodian_fee = round(random.uniform(0.1, 0.2), 4)
                    subscription_fee = round(random.uniform(0, 0.8), 4)
                    redemption_fee = round(random.uniform(0, 0.5), 4)
                    sales_service_fee = round(random.uniform(0.2, 0.4), 4)
                elif fund_type == "混合型":
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
                    "statusCode": 200,
                    "body": {
                        "fundCode": fund_code,
                        "fundName": funds[fund_code]["name"],
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
            
            # 筛选基金
            filtered_funds = []
            for code, fund in funds.items():
                match = True
                
                if fund_type and fund["type"] != fund_type:
                    match = False
                
                if risk_level and fund["risk_level"] != risk_level:
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
                    filtered_funds.append({
                        "fundCode": code,
                        "name": fund["name"],
                        "type": fund["type"],
                        "riskLevel": fund["risk_level"],
                        "company": fund["company"],
                        "industry": fund.get("industry", "多行业")
                    })
            
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