import boto3
import json
import time
import uuid
from datetime import datetime, timedelta
import logging
from typing import List, Optional, Dict, Any
import os

from .models import Message, SessionData

# 配置日志
logger = logging.getLogger(__name__)

# 从环境变量获取会话表名，如果不存在则使用默认值
SESSION_TABLE_NAME = os.getenv("SESSION_TABLE_NAME", "fund-advisor-sessions")
SESSION_TTL_DAYS = int(os.getenv("SESSION_TTL_DAYS", "7"))

# 初始化内存存储作为备份
memory_sessions = {}

# 初始化DynamoDB资源
try:
    dynamodb_resource = boto3.resource('dynamodb')
    logger.info(f"已初始化DynamoDB资源，会话表名：{SESSION_TABLE_NAME}")
except Exception as e:
    logger.error(f"初始化DynamoDB资源失败：{str(e)}")
    # 如果无法连接到DynamoDB，使用内存存储作为备份
    logger.warning("将使用内存存储作为备份")


def create_session(user_id: Optional[str] = None) -> str:
    """
    创建新会话
    
    Args:
        user_id: 用户ID（可选）
        
    Returns:
        str: 会话ID
    """
    session_id = str(uuid.uuid4())
    current_time = int(time.time())
    ttl_timestamp = int((datetime.now() + timedelta(days=SESSION_TTL_DAYS)).timestamp())
    
    session_data = {
        'session_id': session_id,
        'user_id': user_id,
        'messages': [],
        'created_at': current_time,
        'updated_at': current_time,
        'ttl': ttl_timestamp
    }
    
    try:
        table = dynamodb_resource.Table(SESSION_TABLE_NAME)
        table.put_item(Item=session_data)
        logger.info(f"已创建会话：{session_id}")
        return session_id
    except Exception as e:
        logger.error(f"创建会话失败：{str(e)}")
        # 使用内存存储作为备份
        memory_sessions[session_id] = session_data
        return session_id


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """
    获取会话数据
    
    Args:
        session_id: 会话ID
        
    Returns:
        Optional[Dict[str, Any]]: 会话数据，如果不存在则返回None
    """
    try:
        table = dynamodb_resource.Table(SESSION_TABLE_NAME)
        response = table.get_item(Key={'session_id': session_id})
        
        if 'Item' in response:
            logger.info(f"已获取会话：{session_id}")
            return response['Item']
        else:
            logger.warning(f"会话不存在：{session_id}")
            return None
    except Exception as e:
        logger.error(f"获取会话失败：{str(e)}")
        # 使用内存存储作为备份
        return memory_sessions.get(session_id)


def update_session(session_id: str, messages: List[Dict[str, str]]) -> bool:
    """
    更新会话数据
    
    Args:
        session_id: 会话ID
        messages: 消息列表
        
    Returns:
        bool: 更新是否成功
    """
    current_time = int(time.time())
    ttl_timestamp = int((datetime.now() + timedelta(days=SESSION_TTL_DAYS)).timestamp())
    
    # 检查会话是否存在，如果不存在则创建
    session = get_session(session_id)
    if not session:
        logger.info(f"会话不存在，创建新会话：{session_id}")
        # 创建会话数据
        session_data = {
            'session_id': session_id,
            'user_id': None,
            'messages': messages,
            'created_at': current_time,
            'updated_at': current_time,
            'ttl': ttl_timestamp
        }
        
        try:
            table = dynamodb_resource.Table(SESSION_TABLE_NAME)
            table.put_item(Item=session_data)
            logger.info(f"已创建会话：{session_id}")
            return True
        except Exception as e:
            logger.error(f"创建会话失败：{str(e)}")
            # 使用内存存储作为备份
            memory_sessions[session_id] = session_data
            return True
    
    try:
        table = dynamodb_resource.Table(SESSION_TABLE_NAME)
        response = table.update_item(
            Key={'session_id': session_id},
            UpdateExpression="set messages=:m, updated_at=:u, #ttl_attr=:t",
            ExpressionAttributeNames={
                '#ttl_attr': 'ttl'
            },
            ExpressionAttributeValues={
                ':m': messages,
                ':u': current_time,
                ':t': ttl_timestamp
            },
            ReturnValues="UPDATED_NEW"
        )
        logger.info(f"已更新会话：{session_id}")
        return True
    except Exception as e:
        logger.error(f"更新会话失败：{str(e)}")
        # 使用内存存储作为备份
        if session_id in memory_sessions:
            memory_sessions[session_id]['messages'] = messages
            memory_sessions[session_id]['updated_at'] = current_time
            memory_sessions[session_id]['ttl'] = ttl_timestamp
            return True
        else:
            # 如果内存中也没有这个会话，创建一个新的
            session_data = {
                'session_id': session_id,
                'user_id': None,
                'messages': messages,
                'created_at': current_time,
                'updated_at': current_time,
                'ttl': ttl_timestamp
            }
            memory_sessions[session_id] = session_data
            return True


def delete_session(session_id: str) -> bool:
    """
    删除会话
    
    Args:
        session_id: 会话ID
        
    Returns:
        bool: 删除是否成功
    """
    try:
        table = dynamodb_resource.Table(SESSION_TABLE_NAME)
        table.delete_item(Key={'session_id': session_id})
        logger.info(f"已删除会话：{session_id}")
        return True
    except Exception as e:
        logger.error(f"删除会话失败：{str(e)}")
        # 使用内存存储作为备份
        if session_id in memory_sessions:
            del memory_sessions[session_id]
            return True
        return False


def add_message_to_session(session_id: str, role: str, content: str) -> bool:
    """
    向会话添加消息
    
    Args:
        session_id: 会话ID
        role: 消息角色（'user' 或 'assistant'）
        content: 消息内容
        
    Returns:
        bool: 添加是否成功
    """
    session = get_session(session_id)
    if not session:
        logger.warning(f"会话不存在，无法添加消息：{session_id}")
        return False
    
    messages = session.get('messages', [])
    messages.append({'role': role, 'content': content})
    
    return update_session(session_id, messages)


def get_session_messages(session_id: str) -> List[Dict[str, str]]:
    """
    获取会话消息
    
    Args:
        session_id: 会话ID
        
    Returns:
        List[Dict[str, str]]: 消息列表
    """
    session = get_session(session_id)
    if not session:
        logger.warning(f"会话不存在，无法获取消息：{session_id}")
        return []
    
    return session.get('messages', [])


def clear_session_messages(session_id: str) -> bool:
    """
    清除会话消息
    
    Args:
        session_id: 会话ID
        
    Returns:
        bool: 清除是否成功
    """
    return update_session(session_id, [])
