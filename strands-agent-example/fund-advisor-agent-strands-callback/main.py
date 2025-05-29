"""
基金投顾多Agent系统 - 命令行接口

此模块提供了基金投顾多Agent系统的命令行接口，支持使用回调处理器处理各类信息。
"""

import os
import logging
import sys
from dotenv import load_dotenv
from agents.portfolio_manager import PortfolioManagerAgent
from utils.callback_handlers import (
    PrintingCallbackHandler,
    BufferingCallbackHandler,
    EventTrackingCallbackHandler,
    DebugCallbackHandler
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


def main():
    """主程序入口"""
    logger.info("启动基金投顾多Agent系统")
    
    try:
        # 创建投资组合管理Agent
        print("\n" + "="*50)
        print("欢迎使用基金投顾多Agent系统！")
        print("="*50)
        print("\n" + "-"*50)
        print("\n可用的回调处理器模式:")
        print("1. 标准输出模式 (默认)")
        print("2. 事件跟踪模式")
        print("3. 调试模式")
        print("4. 缓冲模式")
        
        # 默认使用标准输出模式
        callback_mode = input("\n请选择回调处理器模式 (1-4，默认为1): ").strip() or "1"
        
        # 根据用户选择创建回调处理器
        callback_handler = None
        if callback_mode == "1":
            print("\n已选择标准输出模式")
            callback_handler = PrintingCallbackHandler()
        elif callback_mode == "2":
            print("\n已选择事件跟踪模式")
            callback_handler = EventTrackingCallbackHandler()
        elif callback_mode == "3":
            print("\n已选择调试模式")
            callback_handler = DebugCallbackHandler()
        elif callback_mode == "4":
            print("\n已选择缓冲模式")
            callback_handler = BufferingCallbackHandler()
        else:
            print("\n无效选择，使用默认的标准输出模式")
            callback_handler = PrintingCallbackHandler()
        
        # 创建投资组合管理Agent，使用选定的回调处理器
        portfolio_manager = PortfolioManagerAgent(callback_handler=callback_handler)
        
        # 启动交互循环
        while True:
            user_input = input("\n请输入您的问题 (输入'退出'结束): ")
            
            # 处理特殊命令
            if user_input.lower() in ['退出', 'exit', 'quit']:
                print("\n感谢使用基金投顾多Agent系统，再见！")
                break
            
            try:
                # 处理用户查询
                print("\n正在处理您的问题，请稍候...\n")
                
                # 如果使用的是缓冲模式，需要特殊处理
                if isinstance(callback_handler, BufferingCallbackHandler):
                    # 重置缓冲区
                    callback_handler.reset()
                    
                    # 处理查询
                    portfolio_manager.process_query(user_input)
                    
                    # 获取缓存的结果
                    result = callback_handler.get_result()
                    
                    # 显示结果
                    print("\n" + "-"*50)
                    print("文本输出:")
                    print(result["text"])
                    print("\n工具使用:")
                    for tool_use in result["tool_uses"]:
                        print(f"- {tool_use['name']}: {tool_use['input']}")
                    print("-"*50)
                else:
                    # 直接处理查询，回调处理器会处理输出
                    response = portfolio_manager.process_query(user_input)
                    
                    # 显示分隔线
                    print("\n" + "-"*50)
            
            except Exception as e:
                logger.error(f"处理查询时出错: {str(e)}")
                print(f"\n处理您的问题时出现错误: {str(e)}")
                print("请尝试重新提问或联系系统管理员。")
    
    except Exception as e:
        logger.error(f"系统启动失败: {str(e)}")
        print(f"系统启动失败: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
