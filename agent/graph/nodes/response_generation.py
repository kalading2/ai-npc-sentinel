from agent.graph.state import AgentState
from agent.llm.llm_client import llm_client
from agent.llm.prompt_templates import RESPONSE_GENERATION_PROMPT
from agent.knowledge.retriever import retrieve_knowledge

async def response_generation(state: AgentState) -> dict:
    perception = state.get("perception_json", {})
    query = f"玩家行为：{perception}，守卫应如何回应？"
    rules = retrieve_knowledge(query)
    if not rules:
        rules = "无特殊规定"
    prompt = RESPONSE_GENERATION_PROMPT.format(
        rules=rules,
        threat_level=state.get("threat_level", "low"),
        animation=state.get("npc_animation", "idle"),
        movement=state.get("npc_movement", "hold_position"),
        perception=str(state.get("perception_json", {})),
        conversation_history="\n".join(state.get("conversation_history", [])),
    )
    dialogue = await llm_client.ainvoke(prompt)
    return {"npc_dialogue": dialogue.strip()}