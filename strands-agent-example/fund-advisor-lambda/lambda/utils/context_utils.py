"""
上下文工具函数，用于获取当前上下文中的callback处理器

此模块提供了用于Lambda环境的上下文工具函数，用于获取和设置当前上下文中的callback处理器。
与Fargate版本相比，此版本已简化，移除了不必要的复杂性。
"""

import logging
import threading
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

def get_current_callback_handler() -> Optional[Callable]:
    """
    获取当前上下文中的callback处理器
    
    在Lambda环境中，我们主要使用线程本地存储来获取callback处理器。
    
    Returns:
        当前上下文中的callback处理器，如果没有则返回None
    """
    try:
        # 尝试从当前线程本地存储获取
        if hasattr(threading.current_thread(), '_callback_handler'):
            handler = getattr(threading.current_thread(), '_callback_handler')
            if handler:
                logger.debug("从线程本地存储获取到callback处理器")
                return handler
    except Exception as e:
        logger.debug(f"无法从线程本地存储获取callback处理器: {e}")
    
    logger.debug("无法获取callback处理器")
    return None

def set_current_callback_handler(handler: Callable) -> None:
    """
    设置当前线程的callback处理器
    
    Args:
        handler: 要设置的callback处理器
    """
    try:
        setattr(threading.current_thread(), '_callback_handler', handler)
        logger.debug("已设置当前线程的callback处理器")
    except Exception as e:
        logger.debug(f"设置当前线程的callback处理器时出错: {e}")
