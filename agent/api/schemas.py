# agent/api/schemas.py
# 请求/响应 Pydantic 数据模型

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


# ---------- 请求模型 ----------

class PerceptionData(BaseModel):
    """UE5 发送的感知数据"""
    player_distance: float = Field(..., description="玩家距离 (cm)")
    player_visible: bool = Field(..., description="玩家是否在视野内")
    player_weapon_drawn: bool = Field(..., description="玩家是否拔出武器")
    time_of_day: str = Field(..., description="白天/黑夜: day / night")
    nearby_allies: int = Field(default=0, description="附近友方NPC数量")
    alarm_triggered: bool = Field(default=False, description="警报是否已激活")
    last_player_action: str = Field(default="none", description="玩家最近一次交互行为")


class PerceptionRequest(BaseModel):
    """UE5 发送的完整请求"""
    npc_id: str = Field(default="guard_atto", description="NPC 唯一标识")
    session_id: str = Field(default="default", description="会话标识")
    perception: PerceptionData = Field(..., description="感知数据")


# ---------- 响应模型 ----------

class ToolCallRecord(BaseModel):
    """工具调用记录"""
    tool_name: str
    arguments: Dict[str, Any]
    result: Optional[str] = None


class InternalState(BaseModel):
    """Agent 内部状态 (调试用)"""
    intent: Optional[str] = None
    threat_level: Optional[str] = None
    memory_updated: bool = False


class DecisionResponse(BaseModel):
    """Agent 返回给 UE5 的决策结果"""
    npc_animation: str = Field(default="idle", description="动画状态")
    npc_dialogue: str = Field(default="", description="NPC 对话/内心独白")
    npc_movement: str = Field(default="hold_position", description="移动指令")
    tool_calls: List[str] = Field(default_factory=list, description="需要调用的工具名称列表")
    internal_state: Optional[InternalState] = None


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    detail: Optional[str] = None