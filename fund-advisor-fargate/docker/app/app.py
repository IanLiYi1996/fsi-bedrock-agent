from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, AsyncIterator
import logging
import os
import sys
import asyncio
from dotenv import load_dotenv

# 添加项目根目录到Python路径，以便导入其他模块
sys.path.append("/app")
from agents.portfolio_manager import PortfolioManagerAgent

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="基金投顾API")

# 创建投资组合管理Agent
portfolio_manager = PortfolioManagerAgent()

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"

@app.get('/health')
def health_check() -> HealthResponse:
    """健康检查端点，用于负载均衡器检测服务状态"""
    return HealthResponse(status="healthy")

@app.post('/advisor')
async def get_investment_advice(request: QueryRequest) -> Dict[str, Any]:
    """获取投资建议的端点"""
    try:
        query = request.query
        if not query:
            raise HTTPException(status_code=400, detail="未提供查询内容")
        
        # 处理用户查询
        logger.info(f"处理用户查询: {query}")
        response = portfolio_manager.process_query(query)
        
        return {
            "response": response,
            "session_id": request.session_id,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"处理查询时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def stream_response(query: str, session_id: Optional[str] = None) -> AsyncIterator[str]:
    """流式返回投资建议"""
    try:
        # 这里需要修改PortfolioManagerAgent以支持流式响应
        # 以下是一个模拟实现
        response = portfolio_manager.process_query(query)
        
        # 模拟流式输出
        chunks = [response[i:i+50] for i in range(0, len(response), 50)]
        for chunk in chunks:
            yield chunk
            await asyncio.sleep(0.1)
    except Exception as e:
        logger.error(f"流式处理查询时出错: {str(e)}")
        yield f"处理您的问题时出现错误: {str(e)}"

@app.post('/advisor/stream')
async def stream_investment_advice(request: QueryRequest):
    """流式返回投资建议的端点"""
    try:
        query = request.query
        if not query:
            raise HTTPException(status_code=400, detail="未提供查询内容")
        
        return StreamingResponse(
            stream_response(query, request.session_id),
            media_type="text/plain"
        )
    except Exception as e:
        logger.error(f"设置流式响应时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    # 这部分代码在使用uvicorn启动时不会执行
    # 仅用于直接运行此文件时的测试
    import uvicorn
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, host='0.0.0.0', port=port)