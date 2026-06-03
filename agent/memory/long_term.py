"""长期记忆，基于 ChromaDB（暂时用模拟实现，后续接入真实向量库）"""
# 模拟存储
_event_store = []

def store_event(npc_id: str, event: str):
    _event_store.append({"npc_id": npc_id, "event": event})

def retrieve_relevant_events(npc_id: str, query: str, top_k: int = 3) -> list[str]:
    # 简单模拟：返回最近的事件
    events = [e["event"] for e in _event_store if e["npc_id"] == npc_id]
    return events[-top_k:]