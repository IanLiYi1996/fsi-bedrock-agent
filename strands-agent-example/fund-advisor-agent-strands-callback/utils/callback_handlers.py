"""
回调处理器模块

此模块提供了各种回调处理器，用于处理 Strands Agents 在执行过程中产生的事件。
这些回调处理器可以用于实时监控、自定义输出格式化和与外部系统集成。
"""

import logging
import json
from typing import Dict, Any, Optional, Callable, List

logger = logging.getLogger(__name__)

class BaseCallbackHandler:
    """基础回调处理器类，提供通用功能"""
    
    def __init__(self):
        """初始化基础回调处理器"""
        self.buffer = ""
        self.current_tool = None
    
    def __call__(self, **kwargs):
        """处理回调事件"""
        # 子类应该重写此方法
        pass
    
    def _handle_text_generation(self, data: str, complete: bool):
        """处理文本生成事件"""
        pass
    
    def _handle_tool_event(self, tool_use: Dict[str, Any]):
        """处理工具使用事件"""
        pass
    
    def _handle_lifecycle_event(self, event_type: str, data: Any):
        """处理生命周期事件"""
        pass
    
    def _handle_reasoning_event(self, reasoning_text: str):
        """处理推理事件"""
        pass


class PrintingCallbackHandler(BaseCallbackHandler):
    """打印回调处理器，将事件输出到控制台"""
    
    def __call__(self, **kwargs):
        """处理回调事件并打印到控制台"""
        # 文本生成事件
        if "data" in kwargs:
            print(kwargs["data"], end="", flush=True)
        
        # 工具使用事件
        elif "current_tool_use" in kwargs and kwargs["current_tool_use"].get("name"):
            tool_name = kwargs["current_tool_use"]["name"]
            print(f"\n[使用工具: {tool_name}]\n", end="", flush=True)
        
        # 完成事件
        elif kwargs.get("complete", False):
            print("\n", end="", flush=True)


class BufferingCallbackHandler(BaseCallbackHandler):
    """缓冲回调处理器，缓存文本直到完成"""
    
    def __init__(self):
        """初始化缓冲回调处理器"""
        super().__init__()
        self.text_buffer = ""
        self.tool_uses = []
        self.complete = False
    
    def __call__(self, **kwargs):
        """处理回调事件并缓存"""
        # 文本生成事件
        if "data" in kwargs:
            self.text_buffer += kwargs["data"]
        
        # 工具使用事件
        elif "current_tool_use" in kwargs and kwargs["current_tool_use"].get("name"):
            tool_use = kwargs["current_tool_use"]
            self.tool_uses.append({
                "name": tool_use.get("name"),
                "input": tool_use.get("input", {})
            })
        
        # 完成事件
        elif kwargs.get("complete", False):
            self.complete = True
    
    def get_result(self) -> Dict[str, Any]:
        """获取缓存的结果"""
        return {
            "text": self.text_buffer,
            "tool_uses": self.tool_uses,
            "complete": self.complete
        }
    
    def reset(self):
        """重置缓存"""
        self.text_buffer = ""
        self.tool_uses = []
        self.complete = False


class StreamingCallbackHandler(BaseCallbackHandler):
    """流式回调处理器，支持实时流式处理"""
    
    def __init__(self, text_callback: Optional[Callable[[str], None]] = None,
                 tool_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
                 complete_callback: Optional[Callable[[], None]] = None):
        """
        初始化流式回调处理器
        
        Args:
            text_callback: 处理文本的回调函数
            tool_callback: 处理工具使用的回调函数
            complete_callback: 处理完成事件的回调函数
        """
        super().__init__()
        self.text_callback = text_callback
        self.tool_callback = tool_callback
        self.complete_callback = complete_callback
    
    def __call__(self, **kwargs):
        """处理回调事件并调用相应的回调函数"""
        # 文本生成事件
        if "data" in kwargs and self.text_callback:
            self.text_callback(kwargs["data"])
        
        # 工具使用事件
        elif "current_tool_use" in kwargs and kwargs["current_tool_use"].get("name") and self.tool_callback:
            self.tool_callback(kwargs["current_tool_use"])
        
        # 完成事件
        elif kwargs.get("complete", False) and self.complete_callback:
            self.complete_callback()


class WebSocketCallbackHandler(BaseCallbackHandler):
    """WebSocket回调处理器，将事件发送到WebSocket连接"""
    
    def __init__(self, send_func: Callable[[str], None]):
        """
        初始化WebSocket回调处理器
        
        Args:
            send_func: 发送消息的函数
        """
        super().__init__()
        self.send_func = send_func
    
    def __call__(self, **kwargs):
        """处理回调事件并发送到WebSocket"""
        event_data = {}
        
        # 文本生成事件
        if "data" in kwargs:
            event_data = {
                "type": "text",
                "content": kwargs["data"]
            }
        
        # 工具使用事件
        elif "current_tool_use" in kwargs and kwargs["current_tool_use"].get("name"):
            event_data = {
                "type": "tool",
                "name": kwargs["current_tool_use"].get("name"),
                "input": kwargs["current_tool_use"].get("input", {})
            }
        
        # 完成事件
        elif kwargs.get("complete", False):
            event_data = {
                "type": "complete",
                "status": "success"
            }
        
        # 发送事件数据
        if event_data:
            self.send_func(json.dumps(event_data))


class DebugCallbackHandler(BaseCallbackHandler):
    """调试回调处理器，记录所有事件"""
    
    def __init__(self, log_level=logging.DEBUG):
        """
        初始化调试回调处理器
        
        Args:
            log_level: 日志级别
        """
        super().__init__()
        self.log_level = log_level
    
    def __call__(self, **kwargs):
        """处理回调事件并记录日志"""
        # 记录所有事件
        logger.log(self.log_level, f"回调事件: {json.dumps(kwargs, default=str)}")


class CompositeCallbackHandler(BaseCallbackHandler):
    """组合回调处理器，将事件分发给多个处理器"""
    
    def __init__(self, handlers: List[BaseCallbackHandler]):
        """
        初始化组合回调处理器
        
        Args:
            handlers: 回调处理器列表
        """
        super().__init__()
        self.handlers = handlers
    
    def __call__(self, **kwargs):
        """处理回调事件并分发给所有处理器"""
        for handler in self.handlers:
            handler(**kwargs)


class SSECallbackHandler(BaseCallbackHandler):
    """Server-Sent Events回调处理器，将事件格式化为SSE格式"""
    
    def __init__(self, send_func: Callable[[str], None]):
        """
        初始化SSE回调处理器
        
        Args:
            send_func: 发送SSE消息的函数
        """
        super().__init__()
        self.send_func = send_func
    
    def __call__(self, **kwargs):
        """处理回调事件并格式化为SSE"""
        # 文本生成事件
        if "data" in kwargs:
            self.send_func(f"data: {kwargs['data']}\n\n")
        
        # 工具使用事件
        elif "current_tool_use" in kwargs and kwargs["current_tool_use"].get("name"):
            tool_name = kwargs["current_tool_use"]["name"]
            self.send_func(f"event: tool\ndata: {tool_name}\n\n")
        
        # 完成事件
        elif kwargs.get("complete", False):
            self.send_func(f"event: complete\ndata: true\n\n")
        
        # 错误事件
        elif kwargs.get("force_stop", False):
            reason = kwargs.get("force_stop_reason", "未知错误")
            self.send_func(f"event: error\ndata: {reason}\n\n")


class EventTrackingCallbackHandler(BaseCallbackHandler):
    """事件跟踪回调处理器，跟踪事件循环生命周期"""
    
    def __init__(self, log_func: Callable[[str], None] = print):
        """
        初始化事件跟踪回调处理器
        
        Args:
            log_func: 记录日志的函数
        """
        super().__init__()
        self.log_func = log_func
    
    def __call__(self, **kwargs):
        """处理回调事件并跟踪生命周期"""
        # 跟踪事件循环生命周期
        if kwargs.get("init_event_loop", False):
            self.log_func("🔄 事件循环初始化")
        elif kwargs.get("start_event_loop", False):
            self.log_func("▶️ 事件循环周期开始")
        elif kwargs.get("start", False):
            self.log_func("📝 新周期开始")
        elif "message" in kwargs:
            self.log_func(f"📬 新消息创建: {kwargs['message'].get('role', 'unknown')}")
        elif kwargs.get("complete", False):
            self.log_func("✅ 周期完成")
        elif kwargs.get("force_stop", False):
            self.log_func(f"🛑 事件循环强制停止: {kwargs.get('force_stop_reason', '未知原因')}")
        
        # 跟踪工具使用
        if "current_tool_use" in kwargs and kwargs["current_tool_use"].get("name"):
            tool_name = kwargs["current_tool_use"]["name"]
            self.log_func(f"🔧 使用工具: {tool_name}")
        
        # 显示文本片段
        if "data" in kwargs:
            # 仅显示每个块的前20个字符
            data_snippet = kwargs["data"][:20] + ("..." if len(kwargs["data"]) > 20 else "")
            self.log_func(f"📟 文本: {data_snippet}")
