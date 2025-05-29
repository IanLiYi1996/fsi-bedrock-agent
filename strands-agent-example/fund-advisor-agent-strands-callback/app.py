"""
基金投顾多Agent系统 - FastAPI接口

此模块提供了基金投顾多Agent系统的FastAPI接口，支持使用回调处理器处理各类信息。
"""

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any, AsyncIterator, List
import logging
import os
import sys
import asyncio
from dotenv import load_dotenv
import json

from agents.portfolio_manager import PortfolioManagerAgent
from utils.callback_handlers import (
    BufferingCallbackHandler,
    StreamingCallbackHandler,
    WebSocketCallbackHandler,
    SSECallbackHandler
)

# 加载环境变量
load_dotenv()
os.environ["KNOWLEDGE_BASE_ID"] = "DDBX9Y6VJ6"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="基金投顾API", description="提供基金投资建议的API服务，支持使用回调处理器处理各类信息")

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
portfolio_manager = None

class QueryRequest(BaseModel):
    """查询请求模型"""
    query: str
    session_id: Optional[str] = None

class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str
    version: str = "1.0.0"

@app.on_event("startup")
async def startup_event():
    """应用启动时执行的事件"""
    global portfolio_manager
    # 创建投资组合管理Agent，不使用回调处理器（将在每个请求中单独创建）
    portfolio_manager = PortfolioManagerAgent(callback_handler=None)
    logger.info("基金投顾API服务已启动")

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
        
        # 创建缓冲回调处理器
        buffer_handler = BufferingCallbackHandler()
        
        # 处理用户查询
        logger.info(f"处理用户查询: {query}")
        portfolio_manager.process_query(query, callback_handler=buffer_handler)
        
        # 获取缓存的结果
        result = buffer_handler.get_result()
        
        return {
            "response": result["text"],
            "tool_uses": result["tool_uses"],
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
    # 创建一个队列用于异步通信
    queue = asyncio.Queue()
    
    # 定义回调函数
    def text_callback(text: str):
        asyncio.create_task(queue.put(text))
    
    def tool_callback(tool_use: Dict[str, Any]):
        tool_name = tool_use.get("name", "未知工具")
        asyncio.create_task(queue.put(f"\n[使用工具: {tool_name}]\n"))
    
    def complete_callback():
        asyncio.create_task(queue.put(None))  # 发送完成信号
    
    # 创建流式回调处理器
    streaming_handler = StreamingCallbackHandler(
        text_callback=text_callback,
        tool_callback=tool_callback,
        complete_callback=complete_callback
    )
    
    try:
        # 在后台处理查询
        asyncio.create_task(
            portfolio_manager.process_query_async(query, callback_handler=streaming_handler)
        )
        
        # 从队列中获取结果并返回
        while True:
            item = await queue.get()
            if item is None:  # 完成信号
                break
            yield item
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
        
        # 创建一个队列用于异步通信
        queue = asyncio.Queue()
        
        # 创建SSE回调处理器
        async def send_sse(data: str):
            await queue.put(data)
        
        sse_handler = SSECallbackHandler(send_func=lambda data: asyncio.create_task(send_sse(data)))
        
        async def event_generator():
            try:
                # 在后台处理查询
                asyncio.create_task(
                    portfolio_manager.process_query_async(query, callback_handler=sse_handler)
                )
                
                # 从队列中获取结果并返回
                while True:
                    item = await queue.get()
                    if item.startswith("event: complete"):
                        yield item
                        break
                    yield item
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

@app.websocket('/ws/advisor')
async def websocket_advisor(websocket: WebSocket):
    """
    WebSocket端点，用于实时交互
    
    Args:
        websocket: WebSocket连接
    """
    await websocket.accept()
    
    try:
        # 创建WebSocket回调处理器
        ws_handler = WebSocketCallbackHandler(
            send_func=lambda data: asyncio.create_task(websocket.send_text(data))
        )
        
        while True:
            # 接收消息
            data = await websocket.receive_text()
            
            try:
                # 解析消息
                message = json.loads(data)
                query = message.get("query")
                
                if not query:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "content": "未提供查询内容"
                    }))
                    continue
                
                logger.info(f"WebSocket处理用户查询: {query}")
                
                # 处理查询
                await portfolio_manager.process_query_async(query, callback_handler=ws_handler)
                
                # 发送完成消息
                await websocket.send_text(json.dumps({
                    "type": "complete",
                    "status": "success"
                }))
            
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "content": "无效的JSON格式"
                }))
            
            except Exception as e:
                logger.error(f"处理WebSocket查询时出错: {str(e)}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "content": str(e)
                }))
    
    except WebSocketDisconnect:
        logger.info("WebSocket连接已断开")
    
    except Exception as e:
        logger.error(f"WebSocket错误: {str(e)}")

if __name__ == '__main__':
    # 这部分代码在使用uvicorn启动时不会执行
    # 仅用于直接运行此文件时的测试
    import uvicorn
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, host='0.0.0.0', port=port)
