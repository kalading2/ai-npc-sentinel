# agent/config.py
# 全局配置管理，从 .env 文件读取所有配置项

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件 (向上查找项目根目录)
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    """全局配置单例"""

    # ---------- LLM 配置 ----------
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    LLM_KIMI: str = os.getenv("LLM_KIMI", "kimi-k2.6")
    LLM_QWEN: str = os.getenv("LLM_QWEN", "qwen3.7-max")
    LLM_EMBEDDING_MODEL:str = os.getenv("LLM_EMBEDDING_MODEL", "text-embedding-v4")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen3.7-max")

    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2048"))

    # ---------- 服务配置 ----------
    AGENT_HOST: str = os.getenv("AGENT_HOST", "0.0.0.0")
    AGENT_PORT: int = int(os.getenv("AGENT_PORT", "8000"))

    # ---------- 记忆配置 ----------
    SHORT_TERM_MEMORY_SIZE: int = int(os.getenv("SHORT_TERM_MEMORY_SIZE", "20"))
    LONG_TERM_MEMORY_TOP_K: int = int(os.getenv("LONG_TERM_MEMORY_TOP_K", "5"))

    # ---------- 知识库配置 ----------
    KNOWLEDGE_TOP_K: int = int(os.getenv("KNOWLEDGE_TOP_K", "3"))

    # ---------- 日志配置 ----------
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # ---------- 最多保留最近上下文历史对话数量 （可根据模型窗口调整）----------
    MAX_HISTORY_LENGTH = 20

    # ---------- 最多保留最近上下文历史对话数量 （可根据模型窗口调整）----------
    MCP_BASE_URL = os.getenv("MCP_BASE_URL", "http://localhost:9000")
    MCP_TIMEOUT = 10.0


# 全局单例
settings = Settings()