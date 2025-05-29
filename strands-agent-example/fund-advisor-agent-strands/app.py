from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any, AsyncIterator
import logging
import os
import sys
import asyncio
from dotenv import load_dotenv

from agents.portfolio_manager import PortfolioManagerAgent

# 加载环境变量
load_dotenv()
os.environ["KNOWLEDGE_BASE_ID"] = "DDBX9Y6VJ6"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="基金投顾API", description="提供基金投资建议的API服务，支持普通查询和流式查询")

# 添加CORS中间件，允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 创建投资组合管理Agent
portfolio_manager = PortfolioManagerAgent(load_tools_from_directory=False)

class QueryRequest(BaseModel):
    """查询请求模型"""
    query: str
    session_id: Optional[str] = None

class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str
    version: str = "1.0.0"

@app.get('/health')
def health_check() -> HealthResponse:
    """健康检查端点，用于负载均衡器检测服务状态"""
    return HealthResponse(status="healthy")

@app.post('/advisor')
async def get_investment_advice(request: QueryRequest) -> Dict[str, Any]:
    """
    获取投资建议的端点
    
    Args:
        request: 包含查询内容和会话ID的请求对象
        
    Returns:
        包含响应内容、会话ID和状态的字典
    """
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

async def stream_response(query: str) -> AsyncIterator[str]:
    """
    流式返回投资建议
    
    Args:
        query: 用户查询内容
        
    Yields:
        文本块或事件数据
    """
    try:
        # 使用我们实现的流式输出功能
        # 直接迭代异步生成器，不要使用await
        async for event in portfolio_manager.process_query_stream(query):
            if "data" in event:
                # 只输出文本内容
                yield event["data"]
            elif "current_tool_use" in event and event["current_tool_use"].get("name"):
                # 可选：输出工具使用信息
                tool_name = event["current_tool_use"]["name"]
                yield f"\n[使用工具: {tool_name}]\n"
    except Exception as e:
        logger.error(f"流式处理查询时出错: {str(e)}")
        yield f"处理您的问题时出现错误: {str(e)}"

@app.post('/advisor/stream')
async def stream_investment_advice(request: QueryRequest):
    """
    流式返回投资建议的端点
    
    Args:
        request: 包含查询内容和会话ID的请求对象
        
    Returns:
        流式响应对象
    """
    try:
        query = request.query
        if not query:
            raise HTTPException(status_code=400, detail="未提供查询内容")
        
        logger.info(f"流式处理用户查询: {query}")
        
        return StreamingResponse(
            stream_response(query),
            media_type="text/plain"
        )
    except Exception as e:
        logger.error(f"设置流式响应时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/')
async def root():
    """返回主页"""
    return FileResponse('static/index.html')

@app.post('/advisor/stream/events')
async def stream_investment_advice_events(request: QueryRequest):
    """
    流式返回投资建议的端点，以Server-Sent Events格式
    
    Args:
        request: 包含查询内容和会话ID的请求对象
        
    Returns:
        SSE格式的流式响应对象
    """
    try:
        query = request.query
        if not query:
            raise HTTPException(status_code=400, detail="未提供查询内容")
        
        logger.info(f"流式处理用户查询(SSE): {query}")
        
        async def event_generator():
            try:
                # 直接迭代异步生成器，不要使用await
                async for event in portfolio_manager.process_query_stream(query):
                    if "data" in event:
                        # 文本内容作为data事件
                        yield f"data: {event['data']}\n\n"
                    elif "current_tool_use" in event and event["current_tool_use"].get("name"):
                        # 工具使用信息作为tool事件
                        tool_name = event["current_tool_use"]["name"]
                        yield f"event: tool\ndata: {tool_name}\n\n"
                
                # 发送完成事件
                yield f"event: complete\ndata: true\n\n"
            except Exception as e:
                logger.error(f"SSE流式处理查询时出错: {str(e)}")
                yield f"event: error\ndata: {str(e)}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
        )
    except Exception as e:
        logger.error(f"设置SSE流式响应时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/advisor/stream/events')
async def stream_investment_advice_events_get(query: str):
    """
    流式返回投资建议的端点（GET方法），以Server-Sent Events格式
    
    Args:
        query: 查询内容
        
    Returns:
        SSE格式的流式响应对象
    """
    try:
        if not query:
            raise HTTPException(status_code=400, detail="未提供查询内容")
        
        logger.info(f"流式处理用户查询(SSE-GET): {query}")
        
        async def event_generator():
            try:
                # 直接迭代异步生成器，不要使用await
                async for event in portfolio_manager.process_query_stream(query):
                    if "data" in event:
                        # 文本内容作为data事件
                        yield f"data: {event['data']}\n\n"
                    elif "current_tool_use" in event and event["current_tool_use"].get("name"):
                        # 工具使用信息作为tool事件
                        tool_name = event["current_tool_use"]["name"]
                        yield f"event: tool\ndata: {tool_name}\n\n"
                
                # 发送完成事件
                yield f"event: complete\ndata: true\n\n"
            except Exception as e:
                logger.error(f"SSE流式处理查询时出错: {str(e)}")
                yield f"event: error\ndata: {str(e)}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
        )
    except Exception as e:
        logger.error(f"设置SSE流式响应时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    # 这部分代码在使用uvicorn启动时不会执行
    # 仅用于直接运行此文件时的测试
    import uvicorn
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, host='0.0.0.0', port=port)
