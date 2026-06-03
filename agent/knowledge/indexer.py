# agent/knowledge/indexer.py
"""
知识库索引构建器。
使用阿里百炼 Embedding API 向量化文档，存储到 ChromaDB。

工作流程：
1. 配置阿里百炼的 Embedding 模型（通过 OpenAI 兼容接口调用）
2. 连接本地 ChromaDB 向量数据库
3. 如果已有索引则直接加载，否则从 documents/ 目录读取文档并构建新索引
4. 索引构建完成后持久化到磁盘，下次启动可直接加载
"""

import os
from pathlib import Path
from loguru import logger

# LlamaIndex 核心组件
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
)
# 阿里百炼 Embedding（兼容 OpenAI 接口）
from llama_index.embeddings.dashscope import DashScopeEmbedding
# ChromaDB 向量存储适配器
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

from agent.config import settings

# ============================================================
# 路径常量
# ============================================================
# 文档目录：放在 knowledge/documents/ 下，放守卫手册等文本文件
DOCUMENTS_DIR = Path(__file__).parent / "documents"
# ChromaDB 持久化目录：项目根目录下的 data/chroma_db/
CHROMA_PERSIST_DIR  = str(Path(__file__).parent.parent.parent / "data" / "chroma_db")

def _setup_enbedding_model():
    """
    配置阿里百炼的 Embedding 模型。

    使用阿里百炼的 text-embedding-v3 模型，通过 OpenAI 兼容接口调用。
    这意味着不需要安装 dashscope SDK，用统一的 OpenAI 协议即可。
    """
    embed_model = DashScopeEmbedding(
        model_name= settings.LLM_EMBEDDING_MODEL,
        api_key=settings.OPENAI_API_KEY,
    )
    logger.info(f"Embedding model loaded: {embed_model.model_name}")
    return embed_model

def build_index(force_rebuild: bool = False) -> VectorStoreIndex:
    """
        构建（或加载）知识库向量索引。

        参数:
            force_rebuild: 是否强制重建索引（删除旧数据，重新从文档生成）

        返回:
            VectorStoreIndex: 可用于检索的向量索引对象

        逻辑:
            1. 先检查 ChromaDB 中是否已有 "guard_rules" 集合
            2. 如果有且不强制重建 → 直接加载已有索引
            3. 如果没有或强制重建 → 从 documents/ 读取文件 → 向量化 → 存入 ChromaDB
        """

    # ---------- 步骤 1：初始化 Embedding 模型 ----------
    embed_model = _setup_enbedding_model()

    # ---------- 步骤 2：连接 ChromaDB ----------
    # PersistentClient：数据持久化到磁盘，重启不丢失
    chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    collection_name ="guard_rules"

    # ---------- 步骤 3：检查是否已有索引 ----------
    existing_collection = chroma_client.list_collections()
    collection_exists = any(c.name == collection_name for c in existing_collection)

    # 情况 A：索引已存在，且不需要重建 → 直接加载
    if not force_rebuild and collection_exists:
        logger.info(f"Loading existing Chroma collection '{collection_name}'")
        chroma_collection = chroma_client.get_collection(collection_name)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        # 从已有的向量存储创建索引对象
        index = VectorStoreIndex.from_vector_store(
            vector_store,
            embed_model=embed_model
        )
        return index

    # 情况 B：需要强制重建，且旧集合存在 → 先删除
    if force_rebuild and collection_exists:
        logger.info(f"Deleting old collection '{collection_name}' for rebuild")
        chroma_client.delete_collection(collection_name)

    # ---------- 步骤 4：创建新集合并构建索引 ----------
    # 创建新集合
    chroma_collection = chroma_client.create_collection(collection_name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    # 检查文档目录是否存在
    if not DOCUMENTS_DIR.exists():
        raise FileNotFoundError(f"Documents directory not found: {DOCUMENTS_DIR}")

    # 读取文档目录下的所有文件（支持 txt、pdf、md 等）
    documents = SimpleDirectoryReader(str(DOCUMENTS_DIR)).load_data()
    logger.info(f"Loaded {len(documents)} documents from {DOCUMENTS_DIR}")

    # 创建存储上下文，绑定 ChromaDB
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    # 核心步骤：将文档向量化并存入 ChromaDB
    # from_documents 内部会：
    #   1. 将文档分块（默认按段落）
    #   2. 调用 Embedding 模型将每个块转成向量
    #   3. 将向量和原始文本存入 ChromaDB
    index = VectorStoreIndex.from_documents(
        documents=documents,
        storage_context=storage_context,
        embed_model=embed_model,
    )
    logger.info("Index built and persisted successfully")

    return index

# ============================================================
# 全局单例：应用启动时自动构建一次
# ============================================================
# 这样后续检索时不需要重复构建，直接复用这个实例
try:
    knowledge_index = build_index()
except Exception as e:
    logger.error(f"Failed to build knowledge index: {e}")
    knowledge_index = None  # 失败时设为 None，检索时会有 fallback 处理