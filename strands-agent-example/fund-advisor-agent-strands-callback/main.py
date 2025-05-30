#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import argparse
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.portfolio_manager import PortfolioManagerAgent
from utils.callback_handlers import ConsoleCallbackHandler, LoggingCallbackHandler, CompositeCallbackHandler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("fund_advisor.log")
    ]
)
logger = logging.getLogger(__name__)

def setup_agent_with_callbacks():
    """
    设置带有回调处理器的投资组合管理Agent
    
    Returns:
        配置好的PortfolioManagerAgent实例
    """
    # 创建投资组合管理Agent
    portfolio_manager = PortfolioManagerAgent()
    
    # 创建回调处理器
    console_handler = ConsoleCallbackHandler()
    logging_handler = LoggingCallbackHandler()
    
    # 使用组合回调处理器
    composite_handler = CompositeCallbackHandler([console_handler, logging_handler])
    
    # 设置回调处理器
    portfolio_manager.agent.callback_handler = composite_handler
    
    return portfolio_manager

def main():
    """主函数"""
    # 加载环境变量
    load_dotenv()
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='基金投资顾问Agent')
    parser.add_argument('--query', '-q', type=str, help='用户查询')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互模式')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出模式')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 设置带有回调处理器的Agent
    portfolio_manager = setup_agent_with_callbacks()
    
    # 处理查询
    if args.query:
        # 单次查询模式
        response = portfolio_manager.process_query(args.query)
        print("\n最终回复:")
        print(response)
    elif args.interactive:
        # 交互模式
        print("欢迎使用基金投资顾问Agent！输入'exit'或'quit'退出。")
        while True:
            try:
                query = input("\n请输入您的问题: ")
                if query.lower() in ['exit', 'quit']:
                    print("谢谢使用，再见！")
                    break
                
                response = portfolio_manager.process_query(query)
                print("\n最终回复:")
                print(response)
            except KeyboardInterrupt:
                print("\n程序被中断，退出...")
                break
            except Exception as e:
                logger.error(f"处理查询时出错: {e}", exc_info=True)
                print(f"处理查询时出错: {e}")
    else:
        # 如果没有提供查询且不是交互模式，显示帮助信息
        parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"程序运行出错: {e}", exc_info=True)
        print(f"程序运行出错: {e}")
        sys.exit(1)
