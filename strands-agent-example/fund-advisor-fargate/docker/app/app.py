#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# 添加项目根目录到Python路径，以便导入其他模块
sys.path.append("/app")
from agents.portfolio_manager import PortfolioManagerAgent
from utils.callback_handlers import StreamingCallbackHandler, LoggingCallbackHandler, EventType
from auth.session import (
    create_session, get_session, update_session, delete_session, 
    add_message_to_session, get_session_messages, clear_session_messages
)

# 加载环境变量
load_dotenv()
# 如果环境变量中没有KNOWLEDGE_BASE_ID，则使用默认值
if "KNOWLEDGE_BASE_ID" not in os.environ:
    os.environ["KNOWLEDGE_BASE_ID"] = "DDBX9Y6VJ6"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("./logs/fund_advisor_api.log")
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

# 请求模型
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    stream: bool = False
    include_events: bool = False

# 响应模型
class QueryResponse(BaseModel):
    response: str
    events: Optional[List[Dict[str, Any]]] = None

# 创建投资组合管理Agent
from utils.context_utils import set_current_callback_handler
from utils.callback_handlers import CompositeCallbackHandler

# 创建回调处理器
logging_handler = LoggingCallbackHandler()
composite_handler = CompositeCallbackHandler([logging_handler])

# 设置线程本地存储的callback处理器
set_current_callback_handler(composite_handler)

# 会话管理
session_managers = {}

def get_portfolio_manager(session_id: str = None):
    """
    获取或创建投资组合管理Agent
    
    Args:
        session_id: 会话ID，如果为None则使用默认会话
        
    Returns:
        PortfolioManagerAgent: 投资组合管理Agent
    """
    if not session_id:
        session_id = "default"
    
    if session_id not in session_managers:
        # 创建新的Agent实例
        agent = PortfolioManagerAgent(callback_handler=composite_handler)
        
        # 加载会话消息
        messages = get_session_messages(session_id)
        if messages:
            # 如果有历史消息，将其直接设置到Agent的messages属性中
            # 由于PortfolioManagerAgent没有load_messages方法，我们直接设置agent.agent.messages
            agent.agent.messages = messages
            logger.info(f"已加载会话消息到Agent: {session_id}, 消息数量: {len(messages)}")
        
        session_managers[session_id] = agent
    
    return session_managers[session_id]

class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"

@app.get("/")
async def root():
    """API根路径，返回API信息"""
    return {
        "name": "基金投资顾问API",
        "version": "1.0.0",
        "description": "基于Strands Agents的基金投资顾问API，提供基金投资建议和分析服务"
    }

@app.get('/health')
def health_check() -> HealthResponse:
    """健康检查端点，用于负载均衡器检测服务状态"""
    return HealthResponse(status="healthy")

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
        # 获取或创建会话ID
        session_id = request.session_id
        if not session_id:
            session_id = create_session()
            logger.info(f"已创建新会话: {session_id}")
        
        # 获取对应的投资组合管理Agent
        portfolio_manager = get_portfolio_manager(session_id)
        
        if request.stream:
            # 流式响应
            return StreamingResponse(
                stream_response(request.query, request.include_events, session_id),
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
            
            # 保存会话消息
            # 由于PortfolioManagerAgent没有get_messages方法，我们直接获取agent.agent.messages
            messages = portfolio_manager.agent.messages
            update_session(session_id, messages)
            
            # 恢复原始回调处理器
            portfolio_manager.agent.callback_handler = original_handler
            
            return QueryResponse(response=response)
    except Exception as e:
        logger.error(f"处理查询时出错: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"处理查询时出错: {str(e)}")

async def stream_response(query: str, include_events: bool = False, session_id: str = None):
    """
    生成流式响应
    
    Args:
        query: 用户查询
        include_events: 是否包含事件信息
        session_id: 会话ID
    
    Yields:
        流式响应数据
    """
    try:
        # 获取对应的投资组合管理Agent
        portfolio_manager = get_portfolio_manager(session_id)
        
        # 创建流式回调处理器
        streaming_handler = StreamingCallbackHandler()
        
        # 设置回调处理器
        original_handler = portfolio_manager.agent.callback_handler
        portfolio_manager.agent.callback_handler = streaming_handler
        
        # 创建异步任务处理查询
        task = asyncio.create_task(process_query_async(query, session_id))
        
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
        
        # 保存会话消息
        if session_id:
            messages = portfolio_manager.agent.messages
            update_session(session_id, messages)
        
        # 恢复原始回调处理器
        portfolio_manager.agent.callback_handler = original_handler
    except Exception as e:
        logger.error(f"流式处理查询时出错: {e}", exc_info=True)
        if include_events:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        else:
            yield f"data: 处理查询时出错: {str(e)}\n\n"

async def process_query_async(query: str, session_id: str = None) -> str:
    """
    异步处理用户查询
    
    Args:
        query: 用户查询
        session_id: 会话ID
    
    Returns:
        处理结果
    """
    # 获取对应的投资组合管理Agent
    portfolio_manager = get_portfolio_manager(session_id)
    
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
    session_id = None
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            
            try:
                # 解析消息
                request_data = json.loads(data)
                query = request_data.get("query", "")
                include_events = request_data.get("include_events", False)
                
                # 获取会话ID
                new_session_id = request_data.get("session_id")
                
                # 如果提供了新的session_id，并且与当前的不同，则更新session_id
                if new_session_id and new_session_id != session_id:
                    if not session_id:
                        logger.info(f"WebSocket连接初始会话: {new_session_id}")
                    else:
                        logger.info(f"WebSocket连接切换会话: {session_id} -> {new_session_id}")
                    session_id = new_session_id
                    await websocket.send_json({"type": "session_info", "session_id": session_id})
                # 如果没有提供session_id，则创建新会话
                elif not session_id:
                    session_id = create_session()
                    logger.info(f"WebSocket连接创建新会话: {session_id}")
                    await websocket.send_json({"type": "session_created", "session_id": session_id})
                
                if not query:
                    await websocket.send_json({"error": "查询不能为空"})
                    continue
                
                # 获取对应的投资组合管理Agent
                portfolio_manager = get_portfolio_manager(session_id)
                
                # 创建流式回调处理器
                streaming_handler = StreamingCallbackHandler()
                
                # 设置回调处理器
                original_handler = portfolio_manager.agent.callback_handler
                portfolio_manager.agent.callback_handler = streaming_handler
                
                # 创建异步任务处理查询
                task = asyncio.create_task(process_query_async(query, session_id))
                
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
                
                # 保存会话消息
                messages = portfolio_manager.agent.messages
                update_session(session_id, messages)
                
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

@app.get("/sse")
async def sse(query: str, session_id: Optional[str] = None, include_events: bool = False):
    """
    SSE端点，用于服务器发送事件
    
    Args:
        query: 用户查询
        session_id: 会话ID
        include_events: 是否包含事件信息
    
    Returns:
        服务器发送的事件流
    """
    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
    }
    
    # 如果没有提供会话ID，则创建新会话
    if not session_id:
        session_id = create_session()
        # 在响应头中添加会话ID
        headers["X-Session-ID"] = session_id
    
    return StreamingResponse(
        stream_response(query, include_events, session_id),
        media_type="text/event-stream",
        headers=headers
    )

# 会话管理API
@app.post("/sessions")
async def create_new_session():
    """
    创建新会话
    
    Returns:
        包含会话ID的对象
    """
    session_id = create_session()
    return {"session_id": session_id}

@app.get("/sessions/{session_id}")
async def get_session_info(session_id: str):
    """
    获取会话信息
    
    Args:
        session_id: 会话ID
    
    Returns:
        会话信息
    """
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"会话不存在: {session_id}")
    return session

@app.delete("/sessions/{session_id}")
async def delete_session_endpoint(session_id: str):
    """
    删除会话
    
    Args:
        session_id: 会话ID
    
    Returns:
        操作结果
    """
    success = delete_session(session_id)
    if not success:
        raise HTTPException(status_code=500, detail=f"删除会话失败: {session_id}")
    
    # 如果会话管理器中存在该会话，也需要删除
    if session_id in session_managers:
        del session_managers[session_id]
    
    return {"status": "success", "message": f"会话已删除: {session_id}"}

@app.delete("/sessions/{session_id}/messages")
async def clear_session_messages_endpoint(session_id: str):
    """
    清除会话消息
    
    Args:
        session_id: 会话ID
    
    Returns:
        操作结果
    """
    success = clear_session_messages(session_id)
    if not success:
        raise HTTPException(status_code=500, detail=f"清除会话消息失败: {session_id}")
    
    # 如果会话管理器中存在该会话，也需要重置其消息
    if session_id in session_managers:
        portfolio_manager = session_managers[session_id]
        # 由于PortfolioManagerAgent没有reset_messages方法，我们直接设置agent.agent.messages为空列表
        portfolio_manager.agent.messages = []
    
    return {"status": "success", "message": f"会话消息已清除: {session_id}"}

if __name__ == '__main__':
    # 这部分代码在使用uvicorn启动时不会执行
    # 仅用于直接运行此文件时的测试
    import uvicorn
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, host='0.0.0.0', port=port)
