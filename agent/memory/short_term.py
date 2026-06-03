"""
短期记忆管理，基于 LangGraph 内置的 MemorySaver + MessagesState。

核心原理：
- LangGraph 的 MemorySaver 会根据 thread_id 自动持久化每次 invoke 后的状态
- 后续调用只需要传入相同的 thread_id，就能拿到之前累积的消息
- 我们只需要"往里追加"，不需要"手动管理列表"
"""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import HumanMessage, AIMessage
from loguru import logger

class ShortTermMemory:
    """
    基于 LangGraph 的短期记忆管理器。

    使用方式：
        memory = ShortTermMemory(max_turns=20)
        memory.add_interaction("玩家靠近了", "我看到了什么...")
        history = memory.get_history()
    """

    def __init__(self, max_turns: int = 20):
        """
        参数:
            max_turns: 保留的最大对话轮数（一轮 = 玩家消息 + NPC 回复）
        """
        self.max_turns = max_turns
        self.checkpointer = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self):
        """
        构建一个极简的状态图。

        这个图只有一个节点，什么都不做，只用于承载消息状态。
        真正的决策逻辑在你的 agent/graph/builder.py 里，这里是独立的记忆存储。
        """
        workflow = StateGraph(MessagesState)
        # 空节点：不做任何处理，只作为状态的载体
        workflow.add_node("save", lambda state: {})
        workflow.add_edge(START, "save")
        workflow.add_edge("save", END)

        # 编译时挂载 checkpointer，自动根据 thread_id 持久化
        return workflow.compile(checkpointer=self.checkpointer)

    def _get_config(self, session_id: str) -> dict:
        """生成 LangGraph 配置（通过 thread_id 隔离不同 NPC/会话）"""
        return {"configurable": {"thread_id": session_id}}

    def _get_current_messages(self, session_id: str) -> list:
        """获取当前会话的所有消息"""
        config = self._get_config(session_id)
        # 传入空消息，LangGraph 会自动从 checkpointer 加载历史状态
        state = self.graph.invoke({"messages": []}, config=config)
        messages = state.get("messages", [])

        # 应用窗口限制：只保留最近 max_turns * 2 条消息
        max_messages = self.max_turns * 2
        if len(messages) > max_messages:
            messages = messages[-max_messages:]

        return messages

    def add_interaction(self, user_msg: str, npc_msg: str, session_id: str = "default"):
        """
        记录一轮对话交互。

        参数:
            user_msg: 玩家输入 / 感知描述
            npc_msg: NPC 的回复
            session_id: 会话 ID（不同 NPC 或不同玩家用不同 ID）
        """
        logger.info("user_msg:"+user_msg+"npc_msg:"+ npc_msg+ "session_id:"+session_id)
        config = self._get_config(session_id)

        # 获取当前消息列表
        current_messages = self._get_current_messages(session_id)

        # 追加新消息
        new_messages = current_messages + [
            HumanMessage(content=user_msg),
            AIMessage(content=npc_msg)
        ]

        # 应用窗口限制
        max_messages = self.max_turns * 2
        if len(new_messages) > max_messages:
            new_messages = new_messages[-max_messages:]

        # 写回状态（相同 thread_id，checkpointer 会保留历史）
        self.graph.invoke({"messages": new_messages}, config=config)

    def get_history(self, session_id: str = "default") -> list[str]:
        """
        获取对话历史，返回字符串列表。
        格式：['玩家: ...', '阿托: ...']
        """
        messages = self._get_current_messages(session_id)
        history = []
        for msg in messages:
            prefix = "玩家" if isinstance(msg, HumanMessage) else "阿托"
            history.append(f"{prefix}: {msg.content}")
        return history

    def reset(self, session_id: str = "default"):
        """
        重置指定会话的记忆。

        LangGraph 的 MemorySaver 没有直接的删除方法，
        因此用空消息覆盖来实现重置。
        """
        config = self._get_config(session_id)
        self.graph.invoke({"messages": []}, config=config)


# 全局单例（你的 routes.py 和 builder.py 可以直接 import 这个实例）
memory = ShortTermMemory(max_turns=20)