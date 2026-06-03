# agent/llm/llm_client.py
# LLM 调用封装，支持 OpenAI 兼容接口 (阿里百炼)
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
from config import settings
from typing import AsyncGenerator

class LLMClient:
    """LLM 调用客户端，使用 OpenAI 兼容接口"""
    def __init__(self):
        self.model = init_chat_model(
            model=settings.LLM_MODEL,
            model_provider="openai",
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )

    async def ainvoke(self, prompt:str, system_prompt:str = "")->str:
        """同步调用 LLM，返回文本结果"""
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        response = await self.model.ainvoke(messages)
        return response.content

    async def astream_generator(self, prompt: str, system_prompt: str = "") -> AsyncGenerator[str, None]:
        """真正的流式生成器，逐个返回 token 块"""
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        async for chunk in self.model.astream(messages):
            content = chunk.content or ""
            if content:
                yield content

llm_client = LLMClient()