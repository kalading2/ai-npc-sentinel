# agent/test_mcp_server.py
"""模拟 UE 端的 MCP Server，用于测试 MCP Client 功能"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="Mock UE MCP Server")

# 模拟工具的实现
TOOL_HANDLERS = {
    "trigger_alarm": lambda **kwargs: {"status": "success", "message": "警报已拉响！"},
    "draw_weapon": lambda **kwargs: {"status": "success", "message": "武器已拔出！"},
    "move_to_location": lambda x, y, **kwargs: {"status": "success", "message": f"移动到坐标 ({x}, {y})"},
    "interrogate_player": lambda **kwargs: {"status": "success", "message": "正在盘查玩家..."},
    "lock_gate": lambda **kwargs: {"status": "success", "message": "城门已锁！"},
    "check_identity": lambda player_id, **kwargs: {"status": "success", "player_id": player_id, "声望": "尊敬"},
}


@app.post("/mcp")
async def handle_mcp(request: Request):
    """模拟 MCP 协议的 JSON-RPC 接口"""
    body = await request.json()
    tool_name = body.get("tool_name", "")
    args = body.get("args", {})

    handler = TOOL_HANDLERS.get(tool_name)
    if handler:
        result = handler(**args)
        return JSONResponse({"status": "success", "result": result})
    else:
        return JSONResponse({"status": "error", "message": f"未知工具: {tool_name}"}, status_code=404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9000)