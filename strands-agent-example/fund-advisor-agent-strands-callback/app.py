#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.portfolio_manager import PortfolioManagerAgent
from utils.callback_handlers import StreamingCallbackHandler, LoggingCallbackHandler, EventType

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("fund_advisor_api.log")
    ]
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="基金投资顾问API",
    description="基于Strands Agents的基金投资顾问API，提供基金投资建议和分析服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 请求模型
class QueryRequest(BaseModel):
    query: str
    stream: bool = False
    include_events: bool = False

# 响应模型
class QueryResponse(BaseModel):
    response: str
    events: Optional[List[Dict[str, Any]]] = None

# 创建投资组合管理Agent
portfolio_manager = PortfolioManagerAgent()

@app.get("/")
async def root():
    """API根路径，返回API信息"""
    return {
        "name": "基金投资顾问API",
        "version": "1.0.0",
        "description": "基于Strands Agents的基金投资顾问API，提供基金投资建议和分析服务"
    }

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    处理用户查询
    
    Args:
        request: 包含用户查询的请求对象
    
    Returns:
        包含响应的对象
    """
    try:
        if request.stream:
            # 流式响应
            return StreamingResponse(
                stream_response(request.query, request.include_events),
                media_type="text/event-stream"
            )
        else:
            # 非流式响应
            # 创建日志回调处理器
            logging_handler = LoggingCallbackHandler()
            
            # 设置回调处理器
            original_handler = portfolio_manager.agent.callback_handler
            portfolio_manager.agent.callback_handler = logging_handler
            
            # 处理查询
            response = portfolio_manager.process_query(request.query)
            
            # 恢复原始回调处理器
            portfolio_manager.agent.callback_handler = original_handler
            
            return QueryResponse(response=response)
    except Exception as e:
        logger.error(f"处理查询时出错: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"处理查询时出错: {str(e)}")

async def stream_response(query: str, include_events: bool = False):
    """
    生成流式响应
    
    Args:
        query: 用户查询
        include_events: 是否包含事件信息
    
    Yields:
        流式响应数据
    """
    try:
        # 创建流式回调处理器
        streaming_handler = StreamingCallbackHandler()
        
        # 设置回调处理器
        original_handler = portfolio_manager.agent.callback_handler
        portfolio_manager.agent.callback_handler = streaming_handler
        
        # 创建异步任务处理查询
        task = asyncio.create_task(process_query_async(query))
        
        # 等待任务完成或超时
        while not task.done():
            # 获取当前事件
            events = streaming_handler.get_events()
            
            # 如果有新事件，发送给客户端
            if events:
                for event in events:
                    if event["type"] == EventType.TEXT:
                        # 文本事件
                        if include_events:
                            yield f"data: {json.dumps({'type': 'text', 'content': event['content']})}\n\n"
                        else:
                            yield f"data: {event['content']}\n\n"
                    elif include_events:
                        # 其他事件，仅在include_events为True时发送
                        yield f"data: {json.dumps(event)}\n\n"
                
                # 清空事件列表
                streaming_handler.events = []
            
            # 等待一小段时间
            await asyncio.sleep(0.1)
        
        # 获取最终结果
        response = await task
        
        # 发送完成事件
        if include_events:
            yield f"data: {json.dumps({'type': 'complete', 'content': response})}\n\n"
        
        # 恢复原始回调处理器
        portfolio_manager.agent.callback_handler = original_handler
    except Exception as e:
        logger.error(f"流式处理查询时出错: {e}", exc_info=True)
        if include_events:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        else:
            yield f"data: 处理查询时出错: {str(e)}\n\n"

async def process_query_async(query: str) -> str:
    """
    异步处理用户查询
    
    Args:
        query: 用户查询
    
    Returns:
        处理结果
    """
    # 使用线程池执行同步操作
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, portfolio_manager.process_query, query)
    return response

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket端点，用于实时交互
    
    Args:
        websocket: WebSocket连接
    """
    await websocket.accept()
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            
            try:
                # 解析消息
                request_data = json.loads(data)
                query = request_data.get("query", "")
                include_events = request_data.get("include_events", False)
                
                if not query:
                    await websocket.send_json({"error": "查询不能为空"})
                    continue
                
                # 创建流式回调处理器
                streaming_handler = StreamingCallbackHandler()
                
                # 设置回调处理器
                original_handler = portfolio_manager.agent.callback_handler
                portfolio_manager.agent.callback_handler = streaming_handler
                
                # 创建异步任务处理查询
                task = asyncio.create_task(process_query_async(query))
                
                # 等待任务完成或超时
                while not task.done():
                    # 获取当前事件
                    events = streaming_handler.get_events()
                    
                    # 如果有新事件，发送给客户端
                    if events:
                        for event in events:
                            if event["type"] == EventType.TEXT:
                                # 文本事件
                                if include_events:
                                    await websocket.send_json({"type": "text", "content": event["content"]})
                                else:
                                    await websocket.send_text(event["content"])
                            elif include_events:
                                # 其他事件，仅在include_events为True时发送
                                await websocket.send_json(event)
                        
                        # 清空事件列表
                        streaming_handler.events = []
                    
                    # 等待一小段时间
                    await asyncio.sleep(0.1)
                
                # 获取最终结果
                response = await task
                
                # 发送完成事件
                if include_events:
                    await websocket.send_json({"type": "complete", "content": response})
                else:
                    await websocket.send_text("\n\n最终回复: " + response)
                
                # 恢复原始回调处理器
                portfolio_manager.agent.callback_handler = original_handler
            
            except json.JSONDecodeError:
                await websocket.send_json({"error": "无效的JSON格式"})
            except Exception as e:
                logger.error(f"WebSocket处理查询时出错: {e}", exc_info=True)
                await websocket.send_json({"error": f"处理查询时出错: {str(e)}"})
    
    except WebSocketDisconnect:
        logger.info("WebSocket连接已关闭")
    except Exception as e:
        logger.error(f"WebSocket连接出错: {e}", exc_info=True)

if __name__ == "__main__":
    import uvicorn
    
    # 获取端口号，默认为8000
    port = int(os.getenv("PORT", "8000"))
    
    # 启动服务器
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
