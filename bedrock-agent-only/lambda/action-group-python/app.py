import json
import logging

# 配置日志
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 模拟图书馆数据库
books = [
    {
        "id": "1",
        "title": "战争与和平",
        "author": "列夫·托尔斯泰",
        "year": 1869,
        "summary": "《战争与和平》是俄国作家列夫·托尔斯泰创作的长篇小说，描述了拿破仑入侵俄国期间俄国社会的各个方面。"
    },
    {
        "id": "2",
        "title": "百年孤独",
        "author": "加西亚·马尔克斯",
        "year": 1967,
        "summary": "《百年孤独》是哥伦比亚作家加西亚·马尔克斯的代表作，讲述了布恩迪亚家族七代人的故事。"
    },
    {
        "id": "3",
        "title": "红楼梦",
        "author": "曹雪芹",
        "year": 1791,
        "summary": "《红楼梦》是中国古典四大名著之一，描述了贾、史、王、薛四大家族的兴衰。"
    },
    {
        "id": "4",
        "title": "傲慢与偏见",
        "author": "简·奥斯汀",
        "year": 1813,
        "summary": "《傲慢与偏见》是英国作家简·奥斯汀的代表作，讲述了伊丽莎白·班内特与达西先生之间的爱情故事。"
    },
    {
        "id": "5",
        "title": "1984",
        "author": "乔治·奥威尔",
        "year": 1949,
        "summary": "《1984》是乔治·奥威尔创作的反乌托邦小说，描述了一个极权主义社会。"
    }
]

def lambda_handler(event, context):
    """
    Lambda处理函数
    """
    logger.info(f"收到的事件: {json.dumps(event)}")
    
    try:
        # 解析API请求
        api_path = event.get('apiPath', '')
        parameters = event.get('parameters', {})
        http_method = event.get('httpMethod', 'GET')
        
        # 处理不同的API路径
        if api_path == '/books' and http_method == 'GET':
            # 获取所有图书
            return {
                "statusCode": 200,
                "body": {
                    "books": [
                        {
                            "id": book["id"],
                            "title": book["title"],
                            "author": book["author"],
                            "year": book["year"]
                        } for book in books
                    ]
                }
            }
        elif api_path.startswith('/books/') and http_method == 'GET':
            # 获取特定ID的图书
            book_id = parameters.get('id') or api_path.split('/')[-1]
            book = next((b for b in books if b["id"] == book_id), None)
            
            if book:
                return {
                    "statusCode": 200,
                    "body": book
                }
            else:
                return {
                    "statusCode": 404,
                    "body": {
                        "message": f"未找到ID为{book_id}的图书"
                    }
                }
        else:
            # 未知的API路径
            return {
                "statusCode": 400,
                "body": {
                    "message": f"不支持的API路径: {api_path}"
                }
            }
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        return {
            "statusCode": 500,
            "body": {
                "message": "处理请求时发生内部错误"
            }
        }
