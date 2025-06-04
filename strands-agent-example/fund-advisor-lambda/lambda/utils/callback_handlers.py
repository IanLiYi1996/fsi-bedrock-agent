"""
回调处理器模块，提供用于处理Agent事件的回调处理器

此模块提供了用于Lambda环境的回调处理器，用于处理Agent事件。
与Fargate版本相比，此版本已简化，移除了流式响应相关的代码。
"""

import json
import logging
from typing import Dict, Any, Optional, List, Callable

logger = logging.getLogger(__name__)

class EventType:
    """事件类型常量"""
    # 基本事件类型
    TEXT = "text"
    TOOL_START = "tool_start"
    TOOL_END = "tool_end"
    
    # 事件循环事件
    INIT_EVENT_LOOP = "init_event_loop"
    START = "start"
    START_EVENT_LOOP = "start_event_loop"
    
    # 消息事件
    MESSAGE_START = "message_start"
    MESSAGE_STOP = "message_stop"
    
    # 内容块事件
    CONTENT_BLOCK_START = "content_block_start"
    CONTENT_BLOCK_DELTA = "content_block_delta"
    CONTENT_BLOCK_STOP = "content_block_stop"
    
    # 元数据事件
    METADATA = "metadata"


class BaseCallbackHandler:
    """基础回调处理器类"""
    
    def __call__(self, **kwargs):
        """处理回调事件"""
        # 事件循环事件
        if "init_event_loop" in kwargs:
            self.on_init_event_loop(kwargs)
        
        if "start" in kwargs and kwargs.get("start") is True:
            self.on_start(kwargs)
        
        if "start_event_loop" in kwargs:
            self.on_start_event_loop(kwargs)
        
        # 消息事件
        if "event" in kwargs:
            event = kwargs.get("event", {})
            
            # 消息开始
            if "messageStart" in event:
                self.on_message_start(event.get("messageStart", {}))
            
            # 内容块开始
            if "contentBlockStart" in event:
                self.on_content_block_start(event.get("contentBlockStart", {}))
            
            # 内容块增量
            if "contentBlockDelta" in event:
                self.on_content_block_delta(event.get("contentBlockDelta", {}))
            
            # 内容块停止
            if "contentBlockStop" in event:
                self.on_content_block_stop(event.get("contentBlockStop", {}))
            
            # 消息停止
            if "messageStop" in event:
                self.on_message_stop(event.get("messageStop", {}))
            
            # 元数据
            if "metadata" in event:
                self.on_metadata(event.get("metadata", {}))
        
        # 处理消息对象
        if "message" in kwargs:
            message = kwargs.get("message", {})
            
            # 处理工具结果
            if message.get("role") == "user" and "content" in message:
                content = message.get("content", [])
                for item in content:
                    if "toolResult" in item:
                        tool_result = item["toolResult"]
                        tool_id = tool_result.get("toolUseId", "")
                        status = tool_result.get("status", "")
                        result_content = tool_result.get("content", [])
                        self.on_tool_result(tool_id, status, result_content)
        
        # 文本生成事件
        if "data" in kwargs:
            self.on_text_generation(kwargs.get("data", ""), kwargs.get("complete", False))
            
            # 处理事件循环指标
            if "event_loop_metrics" in kwargs:
                self.on_event_loop_metrics(kwargs.get("event_loop_metrics", {}))
        
        # 工具使用事件
        if "current_tool_use" in kwargs and kwargs["current_tool_use"].get("name"):
            tool_name = kwargs["current_tool_use"].get("name")
            tool_input = kwargs["current_tool_use"].get("input", {})
            
            # 工具开始使用
            if not kwargs.get("tool_result"):
                self.on_tool_start(tool_name, tool_input)
            # 工具使用结束
            else:
                tool_result = kwargs.get("tool_result", {})
                self.on_tool_end(tool_name, tool_input, tool_result)
        
    
    def on_init_event_loop(self, event_data: Dict[str, Any]):
        """处理事件循环初始化事件"""
        pass
    
    def on_start(self, event_data: Dict[str, Any]):
        """处理开始事件"""
        pass
    
    def on_start_event_loop(self, event_data: Dict[str, Any]):
        """处理事件循环开始事件"""
        pass
    
    def on_message_start(self, message_data: Dict[str, Any]):
        """处理消息开始事件"""
        pass
    
    def on_content_block_start(self, block_data: Dict[str, Any]):
        """处理内容块开始事件"""
        pass
    
    def on_content_block_delta(self, delta_data: Dict[str, Any]):
        """处理内容块增量事件"""
        pass
    
    def on_content_block_stop(self, stop_data: Dict[str, Any]):
        """处理内容块停止事件"""
        pass
    
    def on_message_stop(self, stop_data: Dict[str, Any]):
        """处理消息停止事件"""
        pass
    
    def on_metadata(self, metadata: Dict[str, Any]):
        """处理元数据事件"""
        pass
    
    def on_event_loop_metrics(self, metrics: Dict[str, Any]):
        """处理事件循环指标"""
        pass
    
    def on_text_generation(self, text: str, complete: bool):
        """处理文本生成事件"""
        pass
    
    def on_tool_start(self, tool_name: str, tool_input: Dict[str, Any]):
        """处理工具开始使用事件"""
        pass
    
    def on_tool_end(self, tool_name: str, tool_input: Dict[str, Any], tool_result: Dict[str, Any]):
        """处理工具使用结束事件"""
        pass
    
    
    def on_tool_result(self, tool_id: str, status: str, result_content: List[Dict[str, Any]]):
        """处理工具调用结果事件"""
        pass


class LoggingCallbackHandler(BaseCallbackHandler):
    """日志记录回调处理器"""
    
    def __init__(self, logger_name: str = "agent_callbacks"):
        self.logger = logging.getLogger(logger_name)
    
    def on_init_event_loop(self, event_data: Dict[str, Any]):
        """处理事件循环初始化事件"""
        self.logger.info("事件循环初始化")
    
    def on_start(self, event_data: Dict[str, Any]):
        """处理开始事件"""
        self.logger.info("开始处理")
    
    def on_start_event_loop(self, event_data: Dict[str, Any]):
        """处理事件循环开始事件"""
        self.logger.info("事件循环开始")
    
    def on_message_start(self, message_data: Dict[str, Any]):
        """处理消息开始事件"""
        role = message_data.get("role", "unknown")
        self.logger.info(f"开始 {role} 消息")
    
    def on_content_block_start(self, block_data: Dict[str, Any]):
        """处理内容块开始事件"""
        block_index = block_data.get("contentBlockIndex", 0)
        if "start" in block_data and "toolUse" in block_data["start"]:
            tool_name = block_data["start"]["toolUse"].get("name", "unknown")
            self.logger.info(f"开始内容块 {block_index} (工具使用: {tool_name})")
        else:
            self.logger.info(f"开始内容块 {block_index} (文本)")
    
    def on_content_block_delta(self, delta_data: Dict[str, Any]):
        """处理内容块增量事件"""
        if "delta" in delta_data:
            if "text" in delta_data["delta"]:
                text = delta_data["delta"]["text"]
                self.logger.debug(f"文本增量: {text}")
            elif "toolUse" in delta_data["delta"]:
                tool_input = delta_data["delta"]["toolUse"].get("input", {})
                if tool_input:
                    self.logger.debug(f"工具输入: {json.dumps(tool_input, ensure_ascii=False)}")
    
    def on_content_block_stop(self, stop_data: Dict[str, Any]):
        """处理内容块停止事件"""
        block_index = stop_data.get("contentBlockIndex", 0)
        self.logger.info(f"结束内容块 {block_index}")
    
    def on_message_stop(self, stop_data: Dict[str, Any]):
        """处理消息停止事件"""
        reason = stop_data.get("stopReason", "unknown")
        self.logger.info(f"消息结束，原因: {reason}")
    
    def on_metadata(self, metadata: Dict[str, Any]):
        """处理元数据事件"""
        if "usage" in metadata:
            usage = metadata["usage"]
            self.logger.info(f"使用情况: 输入令牌 {usage.get('inputTokens', 0)}, 输出令牌 {usage.get('outputTokens', 0)}")
        if "metrics" in metadata:
            metrics = metadata["metrics"]
            self.logger.info(f"延迟: {metrics.get('latencyMs', 0)}ms")
    
    def on_event_loop_metrics(self, metrics: Dict[str, Any]):
        """处理事件循环指标"""
        # 可以选择不记录详细指标，避免日志过多
        pass
    
    def on_text_generation(self, text: str, complete: bool):
        """处理文本生成事件"""
        if text:
            self.logger.debug(f"文本生成: {text}")
        if complete:
            self.logger.info("文本生成完成")
    
    def on_tool_start(self, tool_name: str, tool_input: Dict[str, Any]):
        """处理工具开始使用事件"""
        self.logger.info(f"开始使用工具: {tool_name}")
        self.logger.debug(f"工具输入参数: {json.dumps(tool_input, ensure_ascii=False)}")
    
    def on_tool_end(self, tool_name: str, tool_input: Dict[str, Any], tool_result: Dict[str, Any]):
        """处理工具使用结束事件"""
        self.logger.info(f"工具 {tool_name} 执行完成")
        self.logger.debug(f"工具结果: {json.dumps(tool_result, ensure_ascii=False, default=str)}")
    
    
    def on_tool_result(self, tool_id: str, status: str, result_content: List[Dict[str, Any]]):
        """处理工具调用结果事件"""
        self.logger.info(f"工具调用结果 (ID: {tool_id}, 状态: {status})")
        for item in result_content:
            if "text" in item:
                self.logger.info(f"结果内容: {item['text']}")
            else:
                self.logger.debug(f"结果内容: {json.dumps(item, ensure_ascii=False, default=str)}")


class CompositeCallbackHandler(BaseCallbackHandler):
    """组合回调处理器，可以同时使用多个回调处理器"""
    
    def __init__(self, handlers: List[BaseCallbackHandler]):
        self.handlers = handlers
    
    def on_init_event_loop(self, event_data: Dict[str, Any]):
        """处理事件循环初始化事件"""
        for handler in self.handlers:
            handler.on_init_event_loop(event_data)
    
    def on_start(self, event_data: Dict[str, Any]):
        """处理开始事件"""
        for handler in self.handlers:
            handler.on_start(event_data)
    
    def on_start_event_loop(self, event_data: Dict[str, Any]):
        """处理事件循环开始事件"""
        for handler in self.handlers:
            handler.on_start_event_loop(event_data)
    
    def on_message_start(self, message_data: Dict[str, Any]):
        """处理消息开始事件"""
        for handler in self.handlers:
            handler.on_message_start(message_data)
    
    def on_content_block_start(self, block_data: Dict[str, Any]):
        """处理内容块开始事件"""
        for handler in self.handlers:
            handler.on_content_block_start(block_data)
    
    def on_content_block_delta(self, delta_data: Dict[str, Any]):
        """处理内容块增量事件"""
        for handler in self.handlers:
            handler.on_content_block_delta(delta_data)
    
    def on_content_block_stop(self, stop_data: Dict[str, Any]):
        """处理内容块停止事件"""
        for handler in self.handlers:
            handler.on_content_block_stop(stop_data)
    
    def on_message_stop(self, stop_data: Dict[str, Any]):
        """处理消息停止事件"""
        for handler in self.handlers:
            handler.on_message_stop(stop_data)
    
    def on_metadata(self, metadata: Dict[str, Any]):
        """处理元数据事件"""
        for handler in self.handlers:
            handler.on_metadata(metadata)
    
    def on_event_loop_metrics(self, metrics: Dict[str, Any]):
        """处理事件循环指标"""
        for handler in self.handlers:
            handler.on_event_loop_metrics(metrics)
    
    def on_text_generation(self, text: str, complete: bool):
        """处理文本生成事件"""
        for handler in self.handlers:
            handler.on_text_generation(text, complete)
    
    def on_tool_start(self, tool_name: str, tool_input: Dict[str, Any]):
        """处理工具开始使用事件"""
        for handler in self.handlers:
            handler.on_tool_start(tool_name, tool_input)
    
    def on_tool_end(self, tool_name: str, tool_input: Dict[str, Any], tool_result: Dict[str, Any]):
        """处理工具使用结束事件"""
        for handler in self.handlers:
            handler.on_tool_end(tool_name, tool_input, tool_result)
    
    
    def on_tool_result(self, tool_id: str, status: str, result_content: List[Dict[str, Any]]):
        """处理工具调用结果事件"""
        for handler in self.handlers:
            handler.on_tool_result(tool_id, status, result_content)
