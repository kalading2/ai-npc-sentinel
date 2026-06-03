# agent/llm/knowledge_retrieval.py
from agent.graph.state import AgentState
from agent.knowledge.retriever import retrieve_knowledge

async def knowledge_retrieval(state: AgentState) -> dict:
    perception = state.get("perception_json", {})
    # 根据当前情景构造查询
    query = f"玩家行为：{perception},守卫应如何应对？"
    result = retrieve_knowledge(query)
    return {"retrieval_result": result}
