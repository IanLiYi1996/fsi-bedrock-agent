import os
import logging
import sys
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


def main():
    """主程序入口"""
    logger.info("启动基金投顾多Agent系统")
    
    try:
        
        # 创建投资组合管理Agent
        portfolio_manager = PortfolioManagerAgent()
        
        # 启动交互循环
        print("\n" + "="*50)
        print("欢迎使用基金投顾多Agent系统！")
        print("="*50)
        print("\n" + "-"*50)
        
        while True:
            user_input = input("\n请输入您的问题：")
            if user_input.lower() in ['退出', 'exit', 'quit']:
                print("\n感谢使用基金投顾多Agent系统，再见！")
                break
            
            try:
                # 处理用户查询
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

if __name__ == "__main__":
    sys.exit(main())
