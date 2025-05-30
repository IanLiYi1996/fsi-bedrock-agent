"""
上下文工具函数，用于获取当前上下文中的callback处理器
"""

import inspect
import sys
import logging
import gc
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

def get_current_callback_handler() -> Optional[Callable]:
    """
    获取当前上下文中的callback处理器
    
    尝试多种方法获取当前上下文中的callback处理器：
    1. 从strands.context模块获取
    2. 从当前线程本地存储获取
    3. 从调用栈中查找
    
    Returns:
        当前上下文中的callback处理器，如果没有则返回None
    """
    # 方法1: 尝试从strands.context模块获取
    try:
        from strands.context import get_callback_handler
        handler = get_callback_handler()
        if handler:
            logger.debug("从strands.context模块获取到callback处理器")
            return handler
    except (ImportError, AttributeError) as e:
        logger.debug(f"无法从strands.context模块获取callback处理器: {e}")
    
    # 方法2: 尝试从当前线程本地存储获取
    try:
        import threading
        if hasattr(threading.current_thread(), '_callback_handler'):
            handler = getattr(threading.current_thread(), '_callback_handler')
            if handler:
                logger.debug("从线程本地存储获取到callback处理器")
                return handler
    except Exception as e:
        logger.debug(f"无法从线程本地存储获取callback处理器: {e}")
    
    # 方法3: 尝试从调用栈获取
    frame = inspect.currentframe()
    try:
        # 遍历调用栈
        while frame:
            # 检查当前帧的局部变量
            if 'self' in frame.f_locals and hasattr(frame.f_locals['self'], 'callback_handler'):
                handler = frame.f_locals['self'].callback_handler
                if handler:
                    logger.debug("从调用栈获取到callback处理器")
                    return handler
            
            # 检查当前帧的局部变量中是否有callback_handler
            if 'callback_handler' in frame.f_locals:
                handler = frame.f_locals['callback_handler']
                if handler and callable(handler):
                    logger.debug("从调用栈局部变量获取到callback处理器")
                    return handler
            
            # 检查当前帧的全局变量
            if 'callback_handler' in frame.f_globals:
                handler = frame.f_globals['callback_handler']
                if handler and callable(handler):
                    logger.debug("从调用栈全局变量获取到callback处理器")
                    return handler
            
            # 移动到上一帧
            frame = frame.f_back
    except Exception as e:
        logger.debug(f"从调用栈获取callback处理器时出错: {e}")
    finally:
        del frame  # 避免循环引用
    
    # 方法4: 尝试从sys.modules获取
    try:
        for module_name, module in sys.modules.items():
            if module_name.startswith('strands'):
                # 检查模块中是否有Agent类
                if hasattr(module, 'Agent'):
                    agent_class = getattr(module, 'Agent')
                    # 检查Agent类的实例
                    for obj in gc.get_objects():
                        if isinstance(obj, agent_class) and hasattr(obj, 'callback_handler'):
                            handler = obj.callback_handler
                            if handler:
                                logger.debug(f"从{module_name}.Agent实例获取到callback处理器")
                                return handler
    except Exception as e:
        logger.debug(f"从sys.modules获取callback处理器时出错: {e}")
    
    logger.debug("无法获取callback处理器")
    return None

def set_current_callback_handler(handler: Callable) -> None:
    """
    设置当前线程的callback处理器
    
    Args:
        handler: 要设置的callback处理器
    """
    try:
        import threading
        setattr(threading.current_thread(), '_callback_handler', handler)
        logger.debug("已设置当前线程的callback处理器")
    except Exception as e:
        logger.debug(f"设置当前线程的callback处理器时出错: {e}")
