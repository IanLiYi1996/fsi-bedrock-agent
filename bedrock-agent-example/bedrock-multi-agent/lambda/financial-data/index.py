import json
import logging
import random
from datetime import datetime, timedelta

# 配置日志
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 模拟股票数据
stocks = {
    "AAPL": {"name": "Apple Inc.", "sector": "Technology", "current_price": 175.34},
    "MSFT": {"name": "Microsoft Corporation", "sector": "Technology", "current_price": 325.78},
    "GOOGL": {"name": "Alphabet Inc.", "sector": "Technology", "current_price": 135.60},
    "AMZN": {"name": "Amazon.com Inc.", "sector": "Consumer Cyclical", "current_price": 145.22},
    "NVDA": {"name": "NVIDIA Corporation", "sector": "Technology", "current_price": 425.50},
    "TSLA": {"name": "Tesla, Inc.", "sector": "Consumer Cyclical", "current_price": 245.75},
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
        if api_path == '/getStockPrice':
            # 获取股票价格
            ticker = parameters.get('ticker', '').upper()
            if ticker in stocks:
                # 生成模拟价格数据
                today = datetime.now()
                prices = []
                current_price = stocks[ticker]["current_price"]
                
                # 生成过去30天的价格数据
                for i in range(30):
                    date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
                    # 添加一些随机波动
                    price = current_price * (1 + (random.random() - 0.5) * 0.02)
                    prices.append({"date": date, "price": round(price, 2)})
                
                return {
                    "statusCode": 200,
                    "body": {
                        "ticker": ticker,
                        "name": stocks[ticker]["name"],
                        "current_price": stocks[ticker]["current_price"],
                        "historical_prices": prices
                    }
                }
            else:
                return {
                    "statusCode": 404,
                    "body": {
                        "message": f"未找到股票代码 {ticker}"
                    }
                }
        elif api_path == '/getFinancialStatements':
            # 获取财务报表
            ticker = parameters.get('ticker', '').upper()
            if ticker in stocks:
                # 生成模拟财务数据
                return {
                    "statusCode": 200,
                    "body": {
                        "ticker": ticker,
                        "name": stocks[ticker]["name"],
                        "income_statement": {
                            "revenue": round(random.uniform(10000, 100000), 2),
                            "operating_income": round(random.uniform(1000, 30000), 2),
                            "net_income": round(random.uniform(500, 20000), 2)
                        },
                        "balance_sheet": {
                            "total_assets": round(random.uniform(50000, 500000), 2),
                            "total_liabilities": round(random.uniform(20000, 300000), 2),
                            "shareholders_equity": round(random.uniform(10000, 200000), 2)
                        },
                        "cash_flow": {
                            "operating_cash_flow": round(random.uniform(5000, 50000), 2),
                            "investing_cash_flow": round(random.uniform(-30000, -1000), 2),
                            "financing_cash_flow": round(random.uniform(-20000, 10000), 2)
                        }
                    }
                }
            else:
                return {
                    "statusCode": 404,
                    "body": {
                        "message": f"未找到股票代码 {ticker}"
                    }
                }
        elif api_path == '/getMarketSentiment':
            # 获取市场情绪
            ticker = parameters.get('ticker', '').upper()
            if ticker in stocks:
                # 生成模拟情绪数据
                sentiment_score = round(random.uniform(-1, 1), 2)
                sentiment_label = "积极" if sentiment_score > 0.3 else "消极" if sentiment_score < -0.3 else "中性"
                
                return {
                    "statusCode": 200,
                    "body": {
                        "ticker": ticker,
                        "name": stocks[ticker]["name"],
                        "sentiment_score": sentiment_score,
                        "sentiment_label": sentiment_label,
                        "news_count": random.randint(5, 50),
                        "social_media_mentions": random.randint(100, 10000)
                    }
                }
            else:
                return {
                    "statusCode": 404,
                    "body": {
                        "message": f"未找到股票代码 {ticker}"
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