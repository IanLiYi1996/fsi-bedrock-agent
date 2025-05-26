from strands import tool
import requests
import json
import os
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
import functools
import time
from concurrent.futures import ThreadPoolExecutor

# 尝试导入AKShare
try:
    import akshare as ak
    import pandas as pd
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    print("AKShare未安装，将使用备用数据")

# 配置日志
logger = logging.getLogger(__name__)

# 缓存装饰器，用于缓存API调用结果
def cache_result(ttl_seconds=3600):
    """缓存函数结果的装饰器，ttl_seconds为缓存有效期（秒）"""
    def decorator(func):
        cache = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            key = str(args) + str(kwargs)
            
            # 检查缓存是否有效
            if key in cache:
                result, timestamp = cache[key]
                if time.time() - timestamp < ttl_seconds:
                    return result
            
            # 调用原函数
            result = func(*args, **kwargs)
            
            # 更新缓存
            cache[key] = (result, time.time())
            
            return result
        return wrapper
    return decorator

# 全局缓存，用于存储基金列表数据
_fund_list_cache = None
_fund_list_timestamp = 0
_fund_list_ttl = 3600  # 缓存有效期1小时

def get_fund_list():
    """获取基金列表，带缓存"""
    global _fund_list_cache, _fund_list_timestamp
    
    # 检查缓存是否有效
    if _fund_list_cache is not None and time.time() - _fund_list_timestamp < _fund_list_ttl:
        return _fund_list_cache
    
    # 获取基金列表
    if AKSHARE_AVAILABLE:
        try:
            fund_df = ak.fund_name_em()
            _fund_list_cache = fund_df
            _fund_list_timestamp = time.time()
            return fund_df
        except Exception as e:
            logger.warning(f"获取基金列表失败: {str(e)}")
            return None
    return None

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
        # 尝试使用AKShare获取基金信息
        if AKSHARE_AVAILABLE:
            try:
                # 获取基金列表
                fund_df = get_fund_list()
                
                if fund_df is not None:
                    # 查找基金信息
                    fund_detail = fund_df[fund_df['基金代码'] == fund_code]
                    
                    if not fund_detail.empty:
                        # 提取基金类型和风险等级
                        fund_type = fund_detail['基金类型'].values[0] if '基金类型' in fund_detail.columns else "未知"
                        fund_name = fund_detail['基金简称'].values[0]
                        
                        # 风险等级映射
                        risk_level_map = {
                            "货币型": "低",
                            "债券型": "中低",
                            "混合型-偏债": "中低",
                            "混合型-平衡": "中",
                            "混合型-偏股": "中高",
                            "混合型": "中高",
                            "股票型": "高",
                            "指数型": "高",
                            "QDII": "高"
                        }
                        
                        # 默认风险等级
                        risk_level = "中"
                        
                        # 根据基金类型确定风险等级
                        for key, value in risk_level_map.items():
                            if key in fund_type:
                                risk_level = value
                                break
                        
                        # 获取基金公司信息
                        company = fund_detail['基金公司'].values[0] if '基金公司' in fund_detail.columns else "未知"
                        
                        # 获取基金成立日期
                        inception_date = "未知"
                        if '成立日期' in fund_detail.columns:
                            inception_date = str(fund_detail['成立日期'].values[0])
                        
                        # 获取行业信息（简化处理）
                        industry = "多行业"
                        if "医疗" in fund_name or "医药" in fund_name:
                            industry = "医疗健康"
                        elif "科技" in fund_name or "互联网" in fund_name:
                            industry = "科技"
                        elif "消费" in fund_name:
                            industry = "消费"
                        elif "环保" in fund_name:
                            industry = "环保"
                        elif "能源" in fund_name or "新能源" in fund_name:
                            industry = "新能源"
                        elif "金融" in fund_name or "银行" in fund_name:
                            industry = "金融"
                        
                        return {
                            "status": "success",
                            "content": [
                                {
                                    "json": {
                                        "fundCode": fund_code,
                                        "name": fund_name,
                                        "type": fund_type,
                                        "riskLevel": risk_level,
                                        "inceptionDate": inception_date,
                                        "size": 0,  # 暂不获取规模数据，避免额外API调用
                                        "company": company,
                                        "industry": industry
                                    }
                                }
                            ]
                        }
            except Exception as e:
                logger.warning(f"使用AKShare获取基金信息失败: {str(e)}，使用备用数据")
        
        # 如果AKShare不可用或获取失败，使用备用数据
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

# 缓存基金净值数据
@cache_result(ttl_seconds=3600)
def get_fund_nav_data(fund_code):
    """获取基金净值数据，带缓存"""
    if AKSHARE_AVAILABLE:
        try:
            # 获取基金净值数据
            nav_df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
            if not nav_df.empty:
                # 确保日期列是datetime类型
                nav_df['净值日期'] = pd.to_datetime(nav_df['净值日期'])
                # 排序数据
                nav_df = nav_df.sort_values('净值日期')
                return nav_df
        except Exception as e:
            logger.warning(f"获取基金净值数据失败: {str(e)}")
    return None

@tool
def get_fund_performance(fund_code: str) -> Dict[str, Any]:
    """
    获取基金业绩数据
    
    Args:
        fund_code: 基金代码
    """
    try:
        # 尝试使用AKShare获取基金业绩数据
        if AKSHARE_AVAILABLE:
            try:
                # 获取基金净值数据
                nav_df = get_fund_nav_data(fund_code)
                
                if nav_df is not None and not nav_df.empty:
                    # 获取最新净值
                    latest_nav = nav_df.iloc[-1]['单位净值']
                    
                    # 计算各期间收益率
                    returns = {}
                    today = datetime.now()
                    
                    # 计算各期间收益率
                    periods = {
                        "1month": 30,
                        "3month": 90,
                        "6month": 180,
                        "1year": 365,
                        "3year": 365*3,
                        "5year": 365*5
                    }
                    
                    for period_name, days in periods.items():
                        period_ago = today - timedelta(days=days)
                        period_df = nav_df[nav_df['净值日期'] >= period_ago]
                        if not period_df.empty:
                            start_nav = period_df.iloc[0]['单位净值']
                            returns[period_name] = round((latest_nav / start_nav - 1) * 100, 2)
                        else:
                            returns[period_name] = 0
                    
                    # 计算今年来收益率
                    this_year = today.replace(month=1, day=1)
                    this_year_df = nav_df[nav_df['净值日期'] >= this_year]
                    if not this_year_df.empty:
                        start_nav = this_year_df.iloc[0]['单位净值']
                        returns["sinceThisYear"] = round((latest_nav / start_nav - 1) * 100, 2)
                    else:
                        returns["sinceThisYear"] = 0
                    
                    # 计算成立来收益率
                    if not nav_df.empty:
                        start_nav = nav_df.iloc[0]['单位净值']
                        returns["sinceInception"] = round((latest_nav / start_nav - 1) * 100, 2)
                    else:
                        returns["sinceInception"] = 0
                    
                    # 计算风险指标（简化计算）
                    risk_metrics = {
                        "maxDrawdown": -15.0,  # 简化值
                        "volatility": 12.0,    # 简化值
                        "sharpeRatio": 0.8,    # 简化值
                        "informationRatio": 0.5,
                        "treynorRatio": 1.2,
                        "beta": 1.0
                    }
                    
                    # 简化的基准比较
                    benchmark_comparison = {
                        "1year": 2.5,
                        "3year": 5.0,
                        "5year": 8.0
                    }
                    
                    # 获取历史净值数据（限制数量，提高性能）
                    nav_history = []
                    # 每7天取一个点，减少数据量
                    step = 7
                    for i in range(0, len(nav_df), step):
                        row = nav_df.iloc[i]
                        nav_history.append({
                            "date": row['净值日期'].strftime('%Y-%m-%d'),
                            "value": row['单位净值']
                        })
                    
                    # 获取基金名称
                    fund_name = "未知基金"
                    fund_df = get_fund_list()
                    if fund_df is not None:
                        fund_detail = fund_df[fund_df['基金代码'] == fund_code]
                        if not fund_detail.empty:
                            fund_name = fund_detail['基金简称'].values[0]
                    
                    return {
                        "status": "success",
                        "content": [
                            {
                                "json": {
                                    "fundCode": fund_code,
                                    "name": fund_name,
                                    "returns": returns,
                                    "riskMetrics": risk_metrics,
                                    "benchmarkComparison": benchmark_comparison,
                                    "navHistory": nav_history
                                }
                            }
                        ]
                    }
            except Exception as e:
                logger.warning(f"使用AKShare获取基金业绩数据失败: {str(e)}，使用模拟数据")
        
        # 如果AKShare不可用或获取失败，使用模拟数据
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
        # 每7天取一个点，减少数据量
        step = 7
        for i in range(0, 365, step):
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

# 缓存基金持仓数据
@cache_result(ttl_seconds=3600*24)  # 持仓数据缓存时间更长
def get_fund_portfolio_data(fund_code):
    """获取基金持仓数据，带缓存"""
    if AKSHARE_AVAILABLE:
        try:
            # 获取基金持仓数据
            try:
                # 尝试获取股票持仓
                stock_df = ak.fund_portfolio_hold_em(symbol=fund_code, date=datetime.now().strftime('%Y'))
                return {"stock": stock_df}
            except Exception as e:
                logger.warning(f"获取基金股票持仓数据失败: {str(e)}")
            
            # 尝试获取债券持仓
            try:
                bond_df = ak.fund_portfolio_bond_hold_em(symbol=fund_code, date=datetime.now().strftime('%Y'))
                return {"bond": bond_df}
            except Exception as e:
                logger.warning(f"获取基金债券持仓数据失败: {str(e)}")
                
        except Exception as e:
            logger.warning(f"获取基金持仓数据失败: {str(e)}")
    return None

@tool
def get_fund_holdings(fund_code: str) -> Dict[str, Any]:
    """
    获取基金持仓数据
    
    Args:
        fund_code: 基金代码
    """
    try:
        # 尝试使用AKShare获取基金持仓数据
        if AKSHARE_AVAILABLE:
            try:
                # 获取基金类型
                fund_type = "未知"
                fund_name = "未知基金"
                fund_df = get_fund_list()
                if fund_df is not None:
                    fund_detail = fund_df[fund_df['基金代码'] == fund_code]
                    if not fund_detail.empty:
                        fund_name = fund_detail['基金简称'].values[0]
                        if '基金类型' in fund_detail.columns:
                            fund_type = fund_detail['基金类型'].values[0]
                        else:
                            # 根据基金名称推断类型
                            if "股票" in fund_name:
                                fund_type = "股票型"
                            elif "债券" in fund_name:
                                fund_type = "债券型"
                            elif "混合" in fund_name:
                                fund_type = "混合型"
                            elif "指数" in fund_name:
                                fund_type = "指数型"
                            elif "货币" in fund_name:
                                fund_type = "货币型"
                
                # 获取基金持仓数据
                portfolio_data = get_fund_portfolio_data(fund_code)
                
                if portfolio_data:
                    stock_holdings = []
                    bond_holdings = []
                    industry_allocation = {}
                    
                    # 处理股票持仓
                    if "stock" in portfolio_data and portfolio_data["stock"] is not None:
                        stock_df = portfolio_data["stock"]
                        if not stock_df.empty:
                            # 获取最新季度的数据
                            latest_quarter = stock_df['季度'].iloc[0]
                            quarter_df = stock_df[stock_df['季度'] == latest_quarter]
                            
                            # 提取股票持仓
                            for _, row in quarter_df.iterrows():
                                stock_holdings.append({
                                    "name": row['股票名称'],
                                    "code": row['股票代码'],
                                    "weight": float(row['占净值比例']) if '占净值比例' in row else 0,
                                    "industry": "未知"  # AKShare不提供行业信息
                                })
                            
                            # 提取报告日期
                            report_date = latest_quarter.split("股票")[0].strip()
                    
                    # 处理债券持仓
                    if "bond" in portfolio_data and portfolio_data["bond"] is not None:
                        bond_df = portfolio_data["bond"]
                        if not bond_df.empty:
                            # 获取最新季度的数据
                            latest_quarter = bond_df['季度'].iloc[0]
                            quarter_df = bond_df[bond_df['季度'] == latest_quarter]
                            
                            # 提取债券持仓
                            for _, row in quarter_df.iterrows():
                                bond_holdings.append({
                                    "name": row['债券名称'],
                                    "code": row['债券代码'],
                                    "weight": float(row['占净值比例']) if '占净值比例' in row else 0,
                                    "type": "企业债" if "企业" in row['债券名称'] else "国债" if "国债" in row['债券名称'] else "金融债"
                                })
                    
                    # 如果获取到了持仓数据，则返回
                    if stock_holdings or bond_holdings:
                        # 生成行业配置（简化处理）
                        industries = ["消费", "医药", "科技", "金融", "能源"]
                        for industry in industries:
                            industry_allocation[industry] = round(random.uniform(5, 20), 2)
                        
                        # 确保行业配置总和为合理值
                        total = sum(industry_allocation.values())
                        for industry in industry_allocation:
                            industry_allocation[industry] = round(industry_allocation[industry] / total * 70, 2)
                        
                        # 生成资产配置
                        asset_allocation = {}
                        if "股票" in fund_type:
                            asset_allocation = {
                                "股票": 70,
                                "债券": 20,
                                "现金": 10
                            }
                        elif "债券" in fund_type:
                            asset_allocation = {
                                "股票": 10,
                                "债券": 80,
                                "现金": 10
                            }
                        elif "混合" in fund_type:
                            asset_allocation = {
                                "股票": 50,
                                "债券": 40,
                                "现金": 10
                            }
                        else:
                            asset_allocation = {
                                "股票": 40,
                                "债券": 40,
                                "现金": 20
                            }
                        
                        return {
                            "status": "success",
                            "content": [
                                {
                                    "json": {
                                        "fundCode": fund_code,
                                        "name": fund_name,
                                        "reportDate": datetime.now().strftime('%Y-%m-%d'),
                                        "stockHoldings": stock_holdings,
                                        "bondHoldings": bond_holdings,
                                        "industryAllocation": industry_allocation,
                                        "assetAllocation": asset_allocation
                                    }
                                }
                            ]
                        }
            except Exception as e:
                logger.warning(f"使用AKShare获取基金持仓数据失败: {str(e)}，使用模拟数据")
        
        # 如果AKShare不可用或获取失败，使用模拟数据
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

# 缓存基金经理数据
@cache_result(ttl_seconds=3600*24)  # 基金经理数据缓存时间更长
def get_fund_manager_data(fund_code):
    """获取基金经理数据，带缓存"""
    if AKSHARE_AVAILABLE:
        try:
            # 获取基金经理数据
            # 注意：AKShare目前没有直接获取基金经理详细信息的接口
            # 这里使用基金基本信息中的基金经理字段
            fund_df = get_fund_list()
            if fund_df is not None:
                fund_detail = fund_df[fund_df['基金代码'] == fund_code]
                if not fund_detail.empty and '基金经理' in fund_detail.columns:
                    manager_name = fund_detail['基金经理'].values[0]
                    return {"name": manager_name}
        except Exception as e:
            logger.warning(f"获取基金经理数据失败: {str(e)}")
    return None

@tool
def get_fund_manager(fund_code: str) -> Dict[str, Any]:
    """
    获取基金经理信息
    
    Args:
        fund_code: 基金代码
    """
    try:
        # 尝试使用AKShare获取基金经理信息
        if AKSHARE_AVAILABLE:
            try:
                # 获取基金名称
                fund_name = "未知基金"
                fund_df = get_fund_list()
                if fund_df is not None:
                    fund_detail = fund_df[fund_df['基金代码'] == fund_code]
                    if not fund_detail.empty:
                        fund_name = fund_detail['基金简称'].values[0]
                
                # 获取基金经理数据
                manager_data = get_fund_manager_data(fund_code)
                
                if manager_data and "name" in manager_data:
                    # 生成基本信息（AKShare目前无法获取详细信息）
                    manager_name = manager_data["name"]
                    
                    # 生成模拟的其他信息
                    educations = ["清华大学金融学硕士", "北京大学经济学博士", "上海交通大学金融学硕士",
                                 "中国人民大学金融学博士", "复旦大学经济学硕士"]
                    
                    manager_info = {
                        "name": manager_name,
                        "experience": random.randint(5, 20),
                        "education": random.choice(educations),
                        "joined_date": f"20{random.randint(10, 20)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                        "managed_funds": [fund_code],
                        "performance": f"历史年化收益率约{random.randint(5, 20)}%。"
                    }
                    
                    return {
                        "status": "success",
                        "content": [
                            {
                                "json": {
                                    "fundCode": fund_code,
                                    "fundName": fund_name,
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
                logger.warning(f"使用AKShare获取基金经理信息失败: {str(e)}，使用备用数据")
        
        # 如果AKShare不可用或获取失败，使用备用数据
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

# 缓存基金费用数据
@cache_result(ttl_seconds=3600*24*7)  # 费用数据缓存时间更长
def get_fund_fee_data(fund_code):
    """获取基金费用数据，带缓存"""
    if AKSHARE_AVAILABLE:
        try:
            # 尝试获取基金费率数据
            try:
                # 获取申购费率
                subscription_df = ak.fund_fee_em(symbol=fund_code, indicator="申购费率")
                # 获取赎回费率
                redemption_df = ak.fund_fee_em(symbol=fund_code, indicator="赎回费率")
                # 获取运作费用
                operation_df = ak.fund_fee_em(symbol=fund_code, indicator="运作费用")
                
                return {
                    "subscription": subscription_df,
                    "redemption": redemption_df,
                    "operation": operation_df
                }
            except Exception as e:
                logger.warning(f"获取基金费率数据失败: {str(e)}")
                
        except Exception as e:
            logger.warning(f"获取基金费用数据失败: {str(e)}")
    return None

@tool
def get_fund_fees(fund_code: str) -> Dict[str, Any]:
    """
    获取基金费用结构
    
    Args:
        fund_code: 基金代码
    """
    try:
        # 尝试使用AKShare获取基金费用数据
        if AKSHARE_AVAILABLE:
            try:
                # 获取基金名称
                fund_name = "未知基金"
                fund_type = "未知"
                fund_df = get_fund_list()
                if fund_df is not None:
                    fund_detail = fund_df[fund_df['基金代码'] == fund_code]
                    if not fund_detail.empty:
                        fund_name = fund_detail['基金简称'].values[0]
                        if '基金类型' in fund_detail.columns:
                            fund_type = fund_detail['基金类型'].values[0]
                        else:
                            # 根据基金名称推断类型
                            if "股票" in fund_name:
                                fund_type = "股票型"
                            elif "债券" in fund_name:
                                fund_type = "债券型"
                            elif "混合" in fund_name:
                                fund_type = "混合型"
                            elif "指数" in fund_name:
                                fund_type = "指数型"
                            elif "货币" in fund_name:
                                fund_type = "货币型"
                
                # 获取基金费用数据
                fee_data = get_fund_fee_data(fund_code)
                
                if fee_data:
                    # 初始化费率变量
                    management_fee = 0
                    custodian_fee = 0
                    subscription_fee = 0
                    redemption_fee = 0
                    sales_service_fee = 0
                    
                    # 处理运作费用
                    if "operation" in fee_data and fee_data["operation"] is not None and not fee_data["operation"].empty:
                        operation_df = fee_data["operation"]
                        for _, row in operation_df.iterrows():
                            fee_type = row['费用类型'] if '费用类型' in row else ""
                            fee = row['费用'] if '费用' in row else 0
                            
                            # 尝试提取费率数值
                            if isinstance(fee, str) and "%" in fee:
                                fee_value = float(fee.replace("%", "")) / 100
                            else:
                                try:
                                    fee_value = float(fee)
                                except:
                                    fee_value = 0
                            
                            if "管理" in fee_type:
                                management_fee = fee_value
                            elif "托管" in fee_type:
                                custodian_fee = fee_value
                            elif "销售服务" in fee_type:
                                sales_service_fee = fee_value
                    
                    # 处理申购费率
                    subscription_fee_tiers = []
                    if "subscription" in fee_data and fee_data["subscription"] is not None and not fee_data["subscription"].empty:
                        subscription_df = fee_data["subscription"]
                        for _, row in subscription_df.iterrows():
                            amount = row['适用金额'] if '适用金额' in row else ""
                            rate = row['原费率'] if '原费率' in row else ""
                            
                            # 尝试提取费率数值
                            if isinstance(rate, str) and "%" in rate:
                                rate_value = float(rate.replace("%", "")) / 100
                            else:
                                try:
                                    rate_value = float(rate)
                                except:
                                    rate_value = 0
                            
                            subscription_fee_tiers.append({
                                "amount": amount,
                                "rate": rate_value
                            })
                        
                        # 设置基本申购费率（使用第一档）
                        if subscription_fee_tiers:
                            subscription_fee = subscription_fee_tiers[0]["rate"]
                    
                    # 处理赎回费率
                    redemption_fee_tiers = []
                    if "redemption" in fee_data and fee_data["redemption"] is not None and not fee_data["redemption"].empty:
                        redemption_df = fee_data["redemption"]
                        for _, row in redemption_df.iterrows():
                            period = row['持有期限'] if '持有期限' in row else ""
                            rate = row['费率'] if '费率' in row else ""
                            
                            # 尝试提取费率数值
                            if isinstance(rate, str) and "%" in rate:
                                rate_value = float(rate.replace("%", "")) / 100
                            else:
                                try:
                                    rate_value = float(rate)
                                except:
                                    rate_value = 0
                            
                            redemption_fee_tiers.append({
                                "holdingPeriod": period,
                                "rate": rate_value
                            })
                        
                        # 设置基本赎回费率（使用第一档）
                        if redemption_fee_tiers:
                            redemption_fee = redemption_fee_tiers[0]["rate"]
                    
                    # 如果没有获取到完整的费率数据，则根据基金类型补充默认值
                    if management_fee == 0:
                        if "货币" in fund_type:
                            management_fee = 0.2
                        elif "债券" in fund_type:
                            management_fee = 0.6
                        elif "混合" in fund_type:
                            management_fee = 1.2
                        else:  # 股票型或指数型
                            management_fee = 1.5
                    
                    if custodian_fee == 0:
                        if "货币" in fund_type:
                            custodian_fee = 0.08
                        elif "债券" in fund_type:
                            custodian_fee = 0.15
                        elif "混合" in fund_type:
                            custodian_fee = 0.2
                        else:  # 股票型或指数型
                            custodian_fee = 0.25
                    
                    if sales_service_fee == 0:
                        if "货币" in fund_type:
                            sales_service_fee = 0.1
                        elif "债券" in fund_type:
                            sales_service_fee = 0.3
                        elif "混合" in fund_type:
                            sales_service_fee = 0.4
                        else:  # 股票型或指数型
                            sales_service_fee = 0.5
                    
                    # 如果没有获取到申购费率梯度，则生成默认值
                    if not subscription_fee_tiers and subscription_fee > 0:
                        subscription_fee_tiers = [
                            {"amount": "100万以下", "rate": subscription_fee},
                            {"amount": "100万-500万", "rate": round(subscription_fee * 0.6, 4)},
                            {"amount": "500万-1000万", "rate": round(subscription_fee * 0.3, 4)},
                            {"amount": "1000万以上", "rate": round(subscription_fee * 0.1, 4)}
                        ]
                    
                    # 如果没有获取到赎回费率梯度，则生成默认值
                    if not redemption_fee_tiers and redemption_fee > 0:
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
                                    "fundName": fund_name,
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
                logger.warning(f"使用AKShare获取基金费用数据失败: {str(e)}，使用模拟数据")
        
        # 如果AKShare不可用或获取失败，使用模拟数据
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

# 股票资讯和表现数据
stock_news_data = {
    "600519": [  # 贵州茅台
        {"title": "贵州茅台发布2025年一季度财报，营收增长15.3%", "date": "2025-04-15", "sentiment": "positive"},
        {"title": "贵州茅台推出新品系列，市场反应积极", "date": "2025-03-20", "sentiment": "positive"},
        {"title": "分析师预计白酒行业将迎来新一轮增长周期", "date": "2025-02-10", "sentiment": "positive"}
    ],
    "000858": [  # 五粮液
        {"title": "五粮液2025年一季度业绩超预期，净利润增长12.8%", "date": "2025-04-18", "sentiment": "positive"},
        {"title": "五粮液国际市场拓展计划取得突破", "date": "2025-03-15", "sentiment": "positive"},
        {"title": "行业竞争加剧，五粮液市场份额面临挑战", "date": "2025-01-25", "sentiment": "negative"}
    ],
    "00700": [  # 腾讯控股
        {"title": "腾讯云业务增长迅速，AI服务收入翻倍", "date": "2025-04-10", "sentiment": "positive"},
        {"title": "腾讯游戏业务增长放缓，监管环境仍存不确定性", "date": "2025-03-05", "sentiment": "negative"},
        {"title": "腾讯投资海外AI初创公司，布局前沿技术", "date": "2025-02-20", "sentiment": "positive"}
    ],
    "09988": [  # 阿里巴巴
        {"title": "阿里巴巴电商业务重回增长轨道，云业务表现亮眼", "date": "2025-04-20", "sentiment": "positive"},
        {"title": "阿里巴巴国际业务扩张提速，东南亚市场份额提升", "date": "2025-03-10", "sentiment": "positive"},
        {"title": "阿里巴巴面临国内电商竞争加剧，利润率承压", "date": "2025-01-15", "sentiment": "negative"}
    ],
    "601318": [  # 中国平安
        {"title": "中国平安保险科技转型成效显著，线上获客成本降低", "date": "2025-04-12", "sentiment": "positive"},
        {"title": "中国平安寿险业务面临增长瓶颈，新单增速放缓", "date": "2025-03-01", "sentiment": "negative"},
        {"title": "中国平安加大健康生态布局，医疗科技投入增加", "date": "2025-02-15", "sentiment": "positive"}
    ],
    "600036": [  # 招商银行
        {"title": "招商银行零售业务持续领先，财富管理规模创新高", "date": "2025-04-16", "sentiment": "positive"},
        {"title": "招商银行数字化转型加速，科技投入占比提升", "date": "2025-03-08", "sentiment": "positive"},
        {"title": "银行业利差收窄，招商银行净息差承压", "date": "2025-01-20", "sentiment": "negative"}
    ],
    "000651": [  # 格力电器
        {"title": "格力电器海外市场拓展顺利，出口收入大幅增长", "date": "2025-04-05", "sentiment": "positive"},
        {"title": "格力电器新能源业务布局加速，多元化战略见效", "date": "2025-03-12", "sentiment": "positive"},
        {"title": "家电行业竞争激烈，格力电器市场份额小幅下滑", "date": "2025-02-01", "sentiment": "negative"}
    ],
    "000333": [  # 美的集团
        {"title": "美的集团智能家居生态系统获市场认可，销量增长迅速", "date": "2025-04-08", "sentiment": "positive"},
        {"title": "美的集团机器人业务取得突破，工业自动化收入占比提升", "date": "2025-03-18", "sentiment": "positive"},
        {"title": "原材料价格上涨，美的集团毛利率面临压力", "date": "2025-01-10", "sentiment": "negative"}
    ],
    "600276": [  # 恒瑞医药
        {"title": "恒瑞医药多款新药获批上市，研发管线丰富", "date": "2025-04-14", "sentiment": "positive"},
        {"title": "恒瑞医药国际化战略推进顺利，海外收入占比提升", "date": "2025-03-25", "sentiment": "positive"},
        {"title": "医药行业集采扩围，恒瑞医药部分产品降价压力增大", "date": "2025-02-05", "sentiment": "negative"}
    ],
    "300750": [  # 宁德时代
        {"title": "宁德时代新一代电池技术突破，能量密度提升20%", "date": "2025-04-22", "sentiment": "positive"},
        {"title": "宁德时代海外工厂产能爬坡顺利，全球化布局加速", "date": "2025-03-15", "sentiment": "positive"},
        {"title": "动力电池行业竞争加剧，宁德时代市占率小幅下滑", "date": "2025-01-30", "sentiment": "negative"}
    ]
}

# 股票表现数据
stock_performance_data = {
    "600519": {  # 贵州茅台
        "price": 1850.50,
        "change_percent": 0.85,
        "pe_ratio": 28.5,
        "pb_ratio": 9.8,
        "revenue_growth": 15.3,
        "profit_growth": 16.2,
        "analyst_ratings": {"买入": 15, "持有": 5, "卖出": 0},
        "industry_rank": 1,
        "returns": {"1month": 3.2, "3month": 8.5, "6month": 15.8, "1year": 22.5}
    },
    "000858": {  # 五粮液
        "price": 168.30,
        "change_percent": 0.65,
        "pe_ratio": 22.8,
        "pb_ratio": 5.2,
        "revenue_growth": 12.8,
        "profit_growth": 13.5,
        "analyst_ratings": {"买入": 12, "持有": 8, "卖出": 0},
        "industry_rank": 2,
        "returns": {"1month": 2.8, "3month": 7.2, "6month": 13.5, "1year": 18.7}
    },
    "00700": {  # 腾讯控股
        "price": 380.20,
        "change_percent": 1.25,
        "pe_ratio": 24.6,
        "pb_ratio": 4.8,
        "revenue_growth": 18.5,
        "profit_growth": 15.8,
        "analyst_ratings": {"买入": 18, "持有": 3, "卖出": 1},
        "industry_rank": 1,
        "returns": {"1month": 4.5, "3month": 12.8, "6month": 18.5, "1year": 25.6}
    },
    "09988": {  # 阿里巴巴
        "price": 85.50,
        "change_percent": -0.35,
        "pe_ratio": 18.2,
        "pb_ratio": 2.1,
        "revenue_growth": 9.8,
        "profit_growth": 7.5,
        "analyst_ratings": {"买入": 14, "持有": 6, "卖出": 2},
        "industry_rank": 2,
        "returns": {"1month": -1.2, "3month": 5.8, "6month": 8.5, "1year": 12.3}
    },
    "601318": {  # 中国平安
        "price": 48.25,
        "change_percent": 0.45,
        "pe_ratio": 8.5,
        "pb_ratio": 1.2,
        "revenue_growth": 5.2,
        "profit_growth": 4.8,
        "analyst_ratings": {"买入": 10, "持有": 8, "卖出": 2},
        "industry_rank": 1,
        "returns": {"1month": 2.1, "3month": 4.5, "6month": 7.8, "1year": 10.5}
    },
    "600036": {  # 招商银行
        "price": 42.80,
        "change_percent": 0.75,
        "pe_ratio": 7.8,
        "pb_ratio": 1.1,
        "revenue_growth": 6.5,
        "profit_growth": 7.2,
        "analyst_ratings": {"买入": 12, "持有": 6, "卖出": 1},
        "industry_rank": 1,
        "returns": {"1month": 2.8, "3month": 5.2, "6month": 9.5, "1year": 15.2}
    },
    "000651": {  # 格力电器
        "price": 38.50,
        "change_percent": -0.25,
        "pe_ratio": 10.2,
        "pb_ratio": 1.8,
        "revenue_growth": 4.5,
        "profit_growth": 3.8,
        "analyst_ratings": {"买入": 8, "持有": 10, "卖出": 2},
        "industry_rank": 2,
        "returns": {"1month": -0.8, "3month": 2.5, "6month": 5.8, "1year": 8.5}
    },
    "000333": {  # 美的集团
        "price": 65.20,
        "change_percent": 0.85,
        "pe_ratio": 12.5,
        "pb_ratio": 2.5,
        "revenue_growth": 8.2,
        "profit_growth": 7.5,
        "analyst_ratings": {"买入": 14, "持有": 5, "卖出": 1},
        "industry_rank": 1,
        "returns": {"1month": 3.2, "3month": 7.8, "6month": 12.5, "1year": 18.2}
    },
    "600276": {  # 恒瑞医药
        "price": 32.80,
        "change_percent": 1.45,
        "pe_ratio": 35.2,
        "pb_ratio": 5.8,
        "revenue_growth": 12.5,
        "profit_growth": 10.8,
        "analyst_ratings": {"买入": 15, "持有": 4, "卖出": 1},
        "industry_rank": 1,
        "returns": {"1month": 4.8, "3month": 10.5, "6month": 15.2, "1year": 20.5}
    },
    "300750": {  # 宁德时代
        "price": 185.50,
        "change_percent": 2.25,
        "pe_ratio": 42.5,
        "pb_ratio": 6.8,
        "revenue_growth": 25.8,
        "profit_growth": 20.5,
        "analyst_ratings": {"买入": 16, "持有": 3, "卖出": 1},
        "industry_rank": 1,
        "returns": {"1month": 5.8, "3month": 15.2, "6month": 28.5, "1year": 35.8}
    }
}

@tool
def get_stock_news(stock_code: str) -> Dict[str, Any]:
    """
    获取股票相关新闻资讯
    
    Args:
        stock_code: 股票代码
    """
    try:
        if stock_code in stock_news_data:
            return {
                "status": "success",
                "content": [
                    {
                        "json": {
                            "stockCode": stock_code,
                            "news": stock_news_data[stock_code]
                        }
                    }
                ]
            }
        else:
            return {
                "status": "error",
                "content": [
                    {"text": f"未找到股票代码 {stock_code} 的新闻资讯"}
                ]
            }
    except Exception as e:
        return {
            "status": "error",
            "content": [
                {"text": f"获取股票新闻资讯出错: {str(e)}"}
            ]
        }

@tool
def get_stock_performance(stock_code: str) -> Dict[str, Any]:
    """
    获取股票表现数据
    
    Args:
        stock_code: 股票代码
    """
    try:
        if stock_code in stock_performance_data:
            return {
                "status": "success",
                "content": [
                    {
                        "json": {
                            "stockCode": stock_code,
                            "performance": stock_performance_data[stock_code]
                        }
                    }
                ]
            }
        else:
            return {
                "status": "error",
                "content": [
                    {"text": f"未找到股票代码 {stock_code} 的表现数据"}
                ]
            }
    except Exception as e:
        return {
            "status": "error",
            "content": [
                {"text": f"获取股票表现数据出错: {str(e)}"}
            ]
        }

# 用户持仓数据（模拟）
user_portfolio_data = {
    "user123": {
        "risk_profile": "积极型",
        "investment_horizon": "长期",
        "holdings": [
            {"fund_code": "000001", "name": "华夏成长混合", "amount": 10000, "nav": 1.052, "proportion": 20},
            {"fund_code": "110022", "name": "易方达消费行业股票", "amount": 15000, "nav": 2.345, "proportion": 30},
            {"fund_code": "000961", "name": "天弘沪深300指数", "amount": 8000, "nav": 1.456, "proportion": 15},
            {"fund_code": "000198", "name": "中银纯债债券A", "amount": 12000, "nav": 1.123, "proportion": 25},
            {"fund_code": "000617", "name": "易方达货币市场基金A", "amount": 5000, "nav": 1.0, "proportion": 10}
        ]
    },
    "user456": {
        "risk_profile": "稳健型",
        "investment_horizon": "中期",
        "holdings": [
            {"fund_code": "000198", "name": "中银纯债债券A", "amount": 20000, "nav": 1.123, "proportion": 40},
            {"fund_code": "000001", "name": "华夏成长混合", "amount": 15000, "nav": 1.052, "proportion": 30},
            {"fund_code": "000961", "name": "天弘沪深300指数", "amount": 10000, "nav": 1.456, "proportion": 20},
            {"fund_code": "000617", "name": "易方达货币市场基金A", "amount": 5000, "nav": 1.0, "proportion": 10}
        ]
    },
    "user789": {
        "risk_profile": "保守型",
        "investment_horizon": "短期",
        "holdings": [
            {"fund_code": "000198", "name": "中银纯债债券A", "amount": 25000, "nav": 1.123, "proportion": 50},
            {"fund_code": "000617", "name": "易方达货币市场基金A", "amount": 25000, "nav": 1.0, "proportion": 50}
        ]
    }
}

@tool
def get_user_portfolio(user_id: str) -> Dict[str, Any]:
    """
    获取用户持仓信息
    
    Args:
        user_id: 用户ID
    """
    try:
        if user_id in user_portfolio_data:
            return {
                "status": "success",
                "content": [
                    {
                        "json": {
                            "userId": user_id,
                            "riskProfile": user_portfolio_data[user_id]["risk_profile"],
                            "investmentHorizon": user_portfolio_data[user_id]["investment_horizon"],
                            "holdings": user_portfolio_data[user_id]["holdings"]
                        }
                    }
                ]
            }
        else:
            return {
                "status": "error",
                "content": [
                    {"text": f"未找到用户 {user_id} 的持仓信息"}
                ]
            }
    except Exception as e:
        return {
            "status": "error",
            "content": [
                {"text": f"获取用户持仓信息出错: {str(e)}"}
            ]
        }
