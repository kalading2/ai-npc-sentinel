# agent/tools/tool_registry.py
"""
工具注册表，管理所有可被 Agent 调用的 MCP 工具。
支持 OpenAI Function Calling 格式输出。
"""
from typing import Dict, Any, List, Optional


class ToolRegistry:
    """工具注册表，以工具名称为键，存储工具的元数据"""

    def __init__(self) -> None:
        self.tools:Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, description:str, parameters: Optional[Dict[str, Any]] = None,) -> None:
        """
                注册一个工具到注册表。
                :param name: 工具名称（唯一标识）
                :param description: 工具功能的自然语言描述
                :param parameters: OpenAI 兼容的 JSON Schema 参数定义
                """
        self.tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters or {"type": "object", "properties": {}},
        }

    def get_all(self) ->List[str]:
        return list(self.tools.keys())

    def get_tools_for_llm(self)->List[Dict[str, Any]]:
        """返回简洁的工具列表（调试或非 OpenAI 接口使用）"""
        return [
            {
                "name": info["name"],
                "description": info["description"],
                "parameters": info["parameters"],
            }
            for info in self.tools.values()
        ]

    def get_tools_openai_format(self) -> List[Dict[str, Any]]:
        """
                返回 OpenAI Function Calling 所需的完整工具格式。
                可直接喂给 model.bind_tools()。
                """
        return [
            {
                "type": "function",
                "function": {
                    "name": info["name"],
                    "description": info["description"],
                    "parameters": info["parameters"],
                },
            }
            for info in self.tools.values()
        ]

# ============================================================
# 全局单例，预注册城堡守卫阿托可用的工具
# ============================================================
tool_registry = ToolRegistry()

# 1. 拉响警报
tool_registry.register(
    "trigger_alarm",
    "拉响城堡警报，召唤附近卫兵支援",
)

# 2. 拔出武器
tool_registry.register(
    "draw_weapon",
    "拔出武器，进入战斗姿态",
)

# 3. 移动到指定坐标
tool_registry.register(
    "move_to_location",
    "让 NPC 移动到指定坐标",
    {
        "type": "object",
        "properties": {
            "x": {"type": "number", "description": "目标 X 坐标"},
            "y": {"type": "number", "description": "目标 Y 坐标"},
        },
        "required": ["x", "y"],
    },
)