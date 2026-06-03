# agent/graph/builder.py
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from agent.graph.state import AgentState
from agent.graph.nodes.intent_recognition import intent_recognition
from agent.graph.nodes.action_decision import action_decision
from agent.graph.nodes.knowledge_retrieval import knowledge_retrieval
from agent.graph.nodes.threat_assessment import threat_assessment
from agent.graph.nodes.tool_calling import tool_calling


# ========== 条件路由函数 ==========

async def route_by_intent(state: AgentState) -> str:
    """意图识别后的路由"""
    intent = state.get("intent", "chat")
    if intent == "attack":
        return "threat_assessment"
    elif intent in ["warn", "investigate"]:
        return "knowledge_retrieval"
    else:
        # chat 直接到行动决策，省掉威胁评估
        return "action_decision"


async def route_by_threat(state: AgentState) -> str:
    """威胁评估后的路由"""
    threat = state.get("threat_level", "low")
    if threat == "high":
        return "tool_calling"
    else:
        # medium 和 low 都直接行动决策
        return "action_decision"


def build_agent_graph() -> StateGraph:
    builder = StateGraph(AgentState)

    # ========== 添加节点 ==========
    builder.add_node("intent_recognition", intent_recognition)
    builder.add_node("threat_assessment", threat_assessment)
    builder.add_node("knowledge_retrieval", knowledge_retrieval)
    builder.add_node("tool_calling", tool_calling)
    builder.add_node("action_decision", action_decision)

    # ========== 设置入口 ==========
    builder.set_entry_point("intent_recognition")

    # ========== 定义流转 ==========
    builder.add_conditional_edges(
        "intent_recognition",
        route_by_intent,
        {
            "threat_assessment": "threat_assessment",
            "knowledge_retrieval": "knowledge_retrieval",
            "action_decision": "action_decision",
        }
    )

    # 知识检索后 → 威胁评估
    builder.add_edge("knowledge_retrieval", "threat_assessment")

    # 威胁评估后 → 根据等级分支
    builder.add_conditional_edges(
        "threat_assessment",
        route_by_threat,
        {
            "tool_calling": "tool_calling",
            "action_decision": "action_decision",
        }
    )

    # 工具调用后 → 行动决策
    builder.add_edge("tool_calling", "action_decision")

    # 行动决策后结束
    builder.add_edge("action_decision", END)

    # 编译
    memory_saver = MemorySaver()
    graph = builder.compile(checkpointer=memory_saver)
    return graph