# agent/graph/state.py
from typing import TypedDict, Optional

class AgentState(TypedDict):
    # 输入
    perception_json: dict               # 原始感知数据
    # 记忆
    conversation_history: list[str]     # 短期对话历史
    long_term_events: list[str]         # 长期相关记忆
    # 推理
    intent: str                         # 意图：chat / warn / investigate / attack
    threat_level: str                   # 威胁等级：low / medium / high
    retrieval_result: str               # 知识库检索结果
    # 工具调用
    tool_calls: list[dict]              # 需要调用的工具及参数
    tool_results: list[str]             # 工具执行结果
    # 输出
    npc_animation: str                  # npc动作
    npc_dialogue: str                   # npc对话
    npc_movement: str                   # npc移动