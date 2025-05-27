from strands import tool
import akshare as ak

@tool
def get_stock_market_activity() -> dict:
    """Get stock market activity
    Returns:
        stock_market_activity: the stock market activity in JSON format
    """
    try:
        stock_market_activity_legu_df = ak.stock_market_activity_legu()
        return stock_market_activity_legu_df.to_dict(orient='records')
    except Exception as e:
        return {"error": str(e)}
    

@tool
def get_stock_index() -> dict:
    """Get stock index
    Returns:
        stock_index: the stock index in JSON format
    """
    try:
        stock_zh_index_spot_em_df = ak.stock_zh_index_spot_em(symbol="上证系列指数")
        return stock_zh_index_spot_em_df.to_dict(orient='records')
    except Exception as e:
        return {"error": str(e)}
    
@tool
def get_macro_china_lpr() -> dict:
    """Get macro China LPR
    Returns:
        macro_china_lpr: the macro China LPR in JSON format
    """
    try:
        macro_china_lpr_df = ak.macro_china_lpr()
        return macro_china_lpr_df.tail(24).to_dict(orient='records')
    except Exception as e:
        return {"error": str(e)}
    
@tool
def get_macro_china_cpi() -> dict:
    """Get macro China CPI
    Returns:
        macro_china_cpi: the macro China CPI in JSON format
    """
    try:
        macro_china_cpi_df = ak.macro_china_cpi()
        return macro_china_cpi_df.head(24).to_dict(orient='records')
    except Exception as e:
        return {"error": str(e)}

@tool
def get_macro_china_ppi() -> dict:
    """Get macro China PPI
    Returns:
        macro_china_ppi: the macro China PPI in JSON format
    """
    try:
        macro_china_ppi_df = ak.macro_china_ppi()
        return macro_china_ppi_df.tail(24).to_dict(orient='records')
    except Exception as e:
        return {"error": str(e)}