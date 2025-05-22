import os
import logging
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# 导入组件
from knowledge.fund_knowledge import create_knowledge_base
from agents.portfolio_manager import PortfolioManagerAgent

def main():
    """主程序入口"""
    logger.info("启动基金投顾多Agent系统")
    
    try:
        # 创建知识库
        logger.info("创建基金知识库")
        knowledge_agent = create_knowledge_base()
        logger.info("基金知识库创建成功")
        
        # 创建投资组合管理Agent
        logger.info("创建投资组合管理Agent")
        portfolio_manager = PortfolioManagerAgent()
        logger.info("投资组合管理Agent创建成功")
        
        # 启动交互循环
        print("\n" + "="*50)
        print("欢迎使用基金投顾多Agent系统！")
        print("="*50)
        print("\n您可以：")
        print("1. 分析特定基金（例如：'分析基金000001'）")
        print("2. 根据偏好获取推荐（例如：'我是一个风险偏好中等、投资期限3-5年的投资者，请推荐适合我的基金'）")
        print("3. 输入'退出'结束程序")
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
