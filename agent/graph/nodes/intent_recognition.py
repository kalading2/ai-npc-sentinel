# agent/graph/intent_recognition.py
from agent.graph.state import AgentState
from agent.config import settings
from agent.llm.llm_client import llm_client

INTENT_PROMPT = """你是一名经验丰富的城堡守卫。
当前感知信息：{perception}
近期对话历史：{history}
请判断玩家的主要意图，只回复一个单词：
- chat: 单纯交谈
- warn: 需要警告
- investigate: 需要进一步调查
- attack: 准备战斗
"""

async def intent_recognition(state: AgentState) -> dict:
    perception = state.get("perception_json", {})
    history = state.get("conversation_history", {})
    prompt = INTENT_PROMPT.format(
        perception=str(perception),
        history="\n".join(history[-settings.MAX_HISTORY_LENGTH:])
    )

    # 异步调用 LLM
    result = await llm_client.ainvoke(prompt)
    intent = result.strip().lower()

    # 规范化输出
    valid_intents = {"chat", "warn", "investigate", "attack"}
    if intent not in valid_intents:
        intent = "chat"

    return {"intent": intent}