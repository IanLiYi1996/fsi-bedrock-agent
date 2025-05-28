from strands import tool
import akshare as ak

@tool
def get_stock_info_by_code(stock_code: str) -> dict:
    """Get stock details by stock code
    Args:
        stock_code: the code of the stock, e.g., "SH300059"
    Returns:
        stock_details: the details of the stock in JSON format
    """
    try:
        stock_individual_basic_info_xq_df = ak.stock_individual_basic_info_xq(symbol=stock_code)
        return stock_individual_basic_info_xq_df.to_dict(orient='records')
    except Exception as e:
        return {"error": str(e)}

@tool
def get_stock_news_by_code(stock_code: str) -> dict:
    """Get stock news by stock code
    Args:
        stock_code: the code of the stock
    Returns:
        stock_news: the news of the stock in JSON format
    """
    try:
        stock_news_df = ak.stock_news_em(symbol="300059")
        return stock_news_df[["新闻标题"]].head(20).to_dict(orient='records')
    except Exception:
        return {}
    
@tool
def get_stock_performance_by_code(stock_code: str) -> dict:
    """Get stock performance by stock code
    Args:
        stock_code: the code of the stock
    Returns:
        stock_performance: the performance of the stock in JSON format
    """
    try:
        stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
        stock_performance_df = stock_zh_a_spot_em_df[stock_zh_a_spot_em_df['代码'] == stock_code]
        return stock_performance_df.to_dict(orient='records')
    except Exception as e:
        return {"error": str(e)}