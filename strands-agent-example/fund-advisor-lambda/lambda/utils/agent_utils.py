"""
Agent工具函数，用于创建带有父级callback处理器的agent

此模块提供了用于Lambda环境的Agent工具函数，用于创建带有父级callback处理器的agent。
"""

from typing import Dict, Any, Callable, Optional
import logging

logger = logging.getLogger(__name__)

def create_agent_with_parent_callback(agent_class, agent_name: str, parent_callback=None, **kwargs):
    """
    创建带有父级callback处理器的agent
    
    Args:
        agent_class: Agent类
        agent_name: agent名称，用于标识
        parent_callback: 父级callback处理器
        **kwargs: 传递给Agent构造函数的其他参数
    
    Returns:
        创建的Agent实例
    """
    if parent_callback:
        # 创建代理callback处理器
        def proxy_callback(**cb_kwargs):
            # 添加agent标识
            if "data" in cb_kwargs:
                # 文本生成事件，添加前缀
                text = cb_kwargs["data"]
                prefixed_text = f"[{agent_name}] {text}"
                # 调用父级callback处理器，但替换文本
                parent_kwargs = cb_kwargs.copy()
                parent_kwargs["data"] = prefixed_text
                parent_callback(**parent_kwargs)
            # 工具调用事件
            elif "current_tool_use" in cb_kwargs and cb_kwargs["current_tool_use"].get("name"):
                tool_name = cb_kwargs["current_tool_use"].get("name")
                prefixed_tool_name = f"[{agent_name}] {tool_name}"
                # 调用父级callback处理器，但替换工具名称
                parent_kwargs = cb_kwargs.copy()
                parent_kwargs["current_tool_use"] = parent_kwargs["current_tool_use"].copy()
                parent_kwargs["current_tool_use"]["name"] = prefixed_tool_name
                parent_callback(**parent_kwargs)
            # 其他事件
            else:
                # 直接传递给父级callback处理器
                parent_callback(**cb_kwargs)
        
        # 创建Agent，使用代理callback处理器
        return agent_class(callback_handler=proxy_callback, **kwargs)
    else:
        # 如果没有父级callback处理器，直接创建Agent
        return agent_class(**kwargs)
