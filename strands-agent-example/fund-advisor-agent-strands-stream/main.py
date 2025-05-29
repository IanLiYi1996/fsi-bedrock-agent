import os
import logging
import sys
import asyncio
from dotenv import load_dotenv
from agents.portfolio_manager import PortfolioManagerAgent

# 加载环境变量
load_dotenv()
os.environ["KNOWLEDGE_BASE_ID"] = "DDBX9Y6VJ6"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def process_streaming_query(portfolio_manager, user_input):
    """异步处理用户查询并流式输出结果"""
    print("\n正在处理您的问题，请稍候...\n")
    
    try:
        # 获取异步迭代器 - 不需要await，因为process_query_stream返回的是异步生成器
        agent_stream = portfolio_manager.process_query_stream(user_input)
        
        # 处理流式输出
        async for event in agent_stream:
            if "data" in event:
                # 只输出文本内容
                print(event["data"], end="", flush=True)
            elif "current_tool_use" in event and event["current_tool_use"].get("name"):
                # 可选：显示正在使用的工具
                tool_name = event["current_tool_use"]["name"]
                print(f"\n[使用工具: {tool_name}]", end="", flush=True)
        
        print("\n" + "-"*50)
    except Exception as e:
        logger.error(f"处理查询时出错: {str(e)}")
        print(f"\n处理您的问题时出现错误: {str(e)}")
        print("请尝试重新提问或联系系统管理员。")


async def main_async():
    """异步主程序入口"""
    logger.info("启动基金投顾多Agent系统")
    
    try:
        # 创建投资组合管理Agent
        portfolio_manager = PortfolioManagerAgent(load_tools_from_directory=False)
        
        # 启动交互循环
        print("\n" + "="*50)
        print("欢迎使用基金投顾多Agent系统！")
        print("="*50)
        print("\n" + "-"*50)
        print("\n输入 'stream' 开启流式输出模式，输入 'normal' 切换回普通模式")
        
        # 默认使用普通模式
        stream_mode = False
        
        while True:
            user_input = input("\n请输入您的问题：")
            
            # 处理特殊命令
            if user_input.lower() in ['退出', 'exit', 'quit']:
                print("\n感谢使用基金投顾多Agent系统，再见！")
                break
            elif user_input.lower() == 'stream':
                stream_mode = True
                print("\n已切换到流式输出模式")
                continue
            elif user_input.lower() == 'normal':
                stream_mode = False
                print("\n已切换到普通输出模式")
                continue
            
            try:
                # 根据模式选择处理方式
                if stream_mode:
                    # 使用流式输出处理查询
                    await process_streaming_query(portfolio_manager, user_input)
                else:
                    # 使用普通方式处理查询
                    print("\n正在处理您的问题，请稍候...\n")
                    response = portfolio_manager.process_query(user_input)
                    print("\n" + "-"*50)
                    print(response)
                    print("-"*50)
            except Exception as e:
                logger.error(f"处理查询时出错: {str(e)}")
                print(f"\n处理您的问题时出现错误: {str(e)}")
                print("请尝试重新提问或联系系统管理员。")
    
    except Exception as e:
        logger.error(f"系统启动失败: {str(e)}")
        print(f"系统启动失败: {str(e)}")
        return 1
    
    return 0


def main():
    """主程序入口，调用异步主函数"""
    return asyncio.run(main_async())


if __name__ == "__main__":
    sys.exit(main())
