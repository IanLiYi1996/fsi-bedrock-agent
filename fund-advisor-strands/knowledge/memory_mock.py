import logging
from typing import List, Optional, Dict, Any
from strands import tool

logger = logging.getLogger(__name__)

@tool
def memory(action: str, content: Optional[str] = None, query: Optional[str] = None, 
           min_score: float = 0.0, max_results: int = 5, **kwargs) -> Dict[str, Any]:
    """
    模拟memory工具，提供基本的存储和检索功能
    
    Args:
        action: 操作类型，"store"或"retrieve"
        content: 要存储的内容（用于store操作）
        query: 查询内容（用于retrieve操作）
        min_score: 最小相关性分数（用于retrieve操作）
        max_results: 最大结果数（用于retrieve操作）
        **kwargs: 其他参数
    
    Returns:
        Dict[str, Any]: 操作结果
    """
    # 使用全局变量存储文档
    global _documents
    if not hasattr(memory, "_documents"):
        memory._documents = {}
        memory._document_id = 0
    
    if action == "store" and content:
        # 存储内容
        memory._document_id += 1
        doc_id = f"doc_{memory._document_id}"
        memory._documents[doc_id] = content
        logger.info(f"存储文档: {doc_id}")
        return {"status": "success", "document_id": doc_id}
    
    elif action == "retrieve" and query:
        # 检索内容
        results = []
        for doc_id, content in memory._documents.items():
            results.append({
                "document_id": doc_id,
                "content": content,
                "score": 1.0  # 简单起见，所有文档的相关性分数都设为1.0
            })
        
        # 限制结果数量
        results = results[:max_results]
        
        logger.info(f"检索到 {len(results)} 个文档")
        return {"status": "success", "results": results}
    
    else:
        raise ValueError(f"不支持的操作: {action} 或缺少必要参数")
