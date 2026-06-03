# agent/knowledge/retriever.py
"""
知识库检索器。
对外提供简洁的检索接口，内部调用 LlamaIndex 的检索能力。
"""

from loguru import logger
from numpy.ma.core import exp

from agent.knowledge.indexer import knowledge_index

def retrieve_knowledge(query: str,top_k: int = 3) -> str:
    """
        根据查询语句，从知识库中检索最相关的文档片段。

        参数:
            query: 查询文本（自然语言问题）
            top_k: 返回最相关的前 K 个文档片段

        返回:
            str: 拼接后的文档片段，用双换行分隔。如果索引不可用则返回空字符串。

        使用示例:
            result = retrieve_knowledge("夜间如何守卫城门")
            # 返回: "夜间任何人不得靠近城门。\n\n携带武器者必须接受盘查。"
        """
    # 索引未初始化时的 fallback
    if knowledge_index is None:
        logger.warning("Knowledge index is not available, returning empty string")
        return ""

    try:
        # 创建检索器，similarity_top_k 控制返回几个最相关的结果
        retriever = knowledge_index.as_retriever(similarity_top_k=top_k)

        # 执行检索，返回的是 Node 对象列表
        nodes = retriever.retrieve(query)

        # 从每个 Node 中提取原始文本内容
        results = [node.get_content() for node in nodes]

        logger.debug(f"Retrieved {len(results)} chunks for query: {query[:50]}...")

        # 用双换行拼接多个片段，方便 LLM 阅读
        return "\n\n".join(results)

    except Exception as e:
        logger.error(f"Error during knowledge retrieval: {e}")
        return ""