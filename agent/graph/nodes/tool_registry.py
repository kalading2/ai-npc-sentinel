# agent/llm/tool_registry.py
import json
from typing import Dict, Any, List, Optional

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, description: str, parameters: Optional[Dict[str, Any]] = None):
        """注册一个工具"""
        self.tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters or {}
        }

    def get_all(self) -> List[str]:
        """返回所有工具的名称列表（用于简单的 /tools 接口）"""
        return list(self.tools.keys())

    def get_tools_for_llm(self) -> List[Dict[str, Any]]:
        """
        返回适合 LLM 理解的工具描述列表。
        安全处理字段缺失，防止运行时错误。
        """
        tool_list = []
        for tool_info in self.tools.values():
            if not isinstance(tool_info, dict):
                continue
            tool_list.append(
                {
                    "name": tool_info.get("name", ""),
                    "description": tool_info.get("description", ""),
                    "parameters": tool_info.get("parameters", {})
                }
            )

        return tool_list

tool_registry = ToolRegistry()
tool_registry.register("trigger_alarm", "拉响城堡警报")
tool_registry.register("draw_weapon", "拔出武器，进入战斗姿态")
tool_registry.register("move_to_location", "移动到指定坐标", {"type": "object", "properties": {"x": {"type": "number"}, "y": {"type": "number"}}})