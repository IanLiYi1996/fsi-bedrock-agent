from typing import List, Dict, Optional, Any
from pydantic import BaseModel

class Message(BaseModel):
    """会话消息模型"""
    role: str  # 'user' 或 'assistant'
    content: str

class SessionData(BaseModel):
    """会话数据模型"""
    session_id: str
    user_id: Optional[str] = None
    messages: List[Dict[str, str]] = []
    created_at: int
    updated_at: int
    ttl: int
