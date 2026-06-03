# agent/graph/nodes/threat_assessment.py
from agent.graph.state import AgentState
from agent.llm.llm_client import llm_client
from agent.llm.prompt_templates import THREAT_ASSESSMENT_PROMPT
from agent.knowledge.retriever import retrieve_knowledge   # 加这个导入
from agent.config import settings


async def threat_assessment(state: AgentState) -> dict:
    perception = state.get("perception_json", {})
    intent = state.get("intent", "chat")

    # ---------- 关键修改：主动检索知识库 ----------
    query = f"玩家行为：{perception}，意图：{intent}，守卫应如何应对？"
    rules = retrieve_knowledge(query)
    if not rules:
        rules = "无特殊规定"

    memory = state.get("long_term_events", [])

    prompt = THREAT_ASSESSMENT_PROMPT.format(
        perception=str(perception),
        intent=intent,
        rules=rules,                                      # 用主动检索到的规则
        memory="\n".join(memory[settings.MAX_HISTORY_LENGTH:]) if memory else "无"
    )

    result = await llm_client.ainvoke(prompt)
    threat = result.strip().lower()
    if threat not in ["low", "medium", "high"]:
        threat = "low"

    return {
        "threat_level": threat,
        "retrieval_result": rules                         # 顺便传给下游
    }