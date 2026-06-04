# agent/api/routes.py
# FastAPI 路由定义 (先放骨架，后面接入 LangGraph)
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from agent.api.schemas import PerceptionRequest, DecisionResponse, ErrorResponse
from agent.llm.llm_client import llm_client
from agent.memory.short_term import memory
from agent.graph.builder import build_agent_graph
import time
router = APIRouter()
agent_app = build_agent_graph()

@router.post("/decide", response_model=DecisionResponse)
async def decide(req: PerceptionRequest):
    """接收 UE5 感知数据，返回 NPC 行为决策"""
    t0 = time.time()
    # 1. 获取对话历史
    history = memory.get_history(session_id=req.session_id)
    input_state = {
        "perception_json": req.perception.model_dump(),
        "conversation_history": history,
        "long_term_events": [],
    }
    config = {"configurable": {"thread_id": req.session_id}}
    result = await agent_app.ainvoke(input_state, config)

    # 记录对话
    npc_dialogue = result.get("npc_dialogue", "...")
    memory.add_interaction(
        user_msg=f"感知：{req.perception.model_dump()}",
        npc_msg=npc_dialogue,
        session_id=req.session_id
    )
    t1 = time.time()
    print(f"[TIMING] /decide 总耗时: {t1 - t0:.2f}秒")
    return DecisionResponse(
        npc_animation=result.get("npc_animation", "idle"),
        npc_dialogue=npc_dialogue,
        npc_movement=result.get("npc_movement", "hold_position"),
        tool_calls=[tc["tool"] for tc in result.get("tool_calls", [])],
        internal_state={
            "intent": result.get("intent"),
            "threat_level": result.get("threat_level")
        }
    )


@router.post("/decide/stream")
async def decide_stream(req: PerceptionRequest):
    """
    流式决策接口：返回 SSE 事件流，每个事件包含一个 NPC 对话 token。
    UE 端可以逐步显示对话，实现边说边显示的效果。
    """
    # 1. 组装 prompt（这里可以接入 LangGraph，暂时直接调 LLM）
    perception = req.perception.model_dump()
    prompt = f"当前环境感知：{perception}。请以哨兵阿托的身份，说一句话。"
    system_prompt = "你是城堡守卫阿托，说话简洁有力。"

    # 2. 异步生成器，将 LLM token 包装成 SSE 格式
    async def event_stream():
        async for token in llm_client.astream_generator(prompt,system_prompt):
            # SSE 格式: data: <内容>\n\n
            yield f"data:{token}\n\n"
        # 流结束标识（可选）
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲
        }
    )


@router.post("/reset/{npc_id}")
async def reset_npc(npc_id: str):
    """重置指定 NPC 的记忆"""
    memory.reset()
    return {"status": "ok", "npc_id": npc_id, "message": "记忆已重置"}


@router.get("/tools")
async def list_tools():
    """列出所有可用工具"""
    from agent.tools.tool_registry import tool_registry
    return {"tools": tool_registry.get_all()}