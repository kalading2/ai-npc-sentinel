# agent/api/action_decision.py
import json
from agent.graph.state import AgentState
from agent.llm.llm_client import llm_client
from agent.llm.prompt_templates import ACTION_DECISION_PROMPT

async def action_decision(state: AgentState) -> dict:
    threat = state.get("threat_level", "low")
    intent = state.get("intent","chat")
    perception = state.get("perception_json", {})
    tool_results = state.get("tool_results", [])

    # 1. 构造 Prompt
    prompt = ACTION_DECISION_PROMPT.format(
        threat_level=threat,
        intent=intent,
        perception=str(perception),
        tool_results="；".join(tool_results) if tool_results else "无"
    )
    # 2. 调用 LLM
    result = await llm_client.ainvoke(prompt)

    # 3. 解析返回的 JSON 字符串
    try:
        cleaned = result.strip()
        # 处理可能的 markdown 代码块
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = [l for l in lines if not l.startswith("```")]
            cleaned = "\n".join(lines)
        decision = json.loads(cleaned)
    except json.JSONDecodeError:
        decision =  {"animation": "alert", "movement": "hold_position", "dialogue": "..."}

    return {
        "npc_animation": decision.get("animation", "idle"),
        "npc_movement": decision.get("movement", "hold_position"),
        "npc_dialogue": decision.get("dialogue", "...")
    }
