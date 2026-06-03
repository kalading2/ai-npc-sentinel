# agent/tools/mcp_client.py
"""MCP 客户端，负责与 UE 端的 MCP Server 通信"""
import httpx
from loguru import logger
from agent.config import settings

class MCPClient:
    """MCP 协议客户端"""
    def __init__(self, base_url: str = None):
        self.base_url = base_url or getattr(settings, 'MCP_SERVER_URL', settings.MCP_BASE_URL)
        self.timeout = settings.MCP_TIMEOUT

    async def call_tool(self, tool_name: str, args: dict = None) -> dict:
        """调用 MCP Server 上的工具"""
        payload = {
            "tool_name": tool_name,
            "args": args or {},
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/mcp", json=payload)
                response.raise_for_status()
                result = response.json()
                logger.info(f"[MCP] 调用工具: {tool_name}, 参数: {result}")
                return result
        except httpx.HTTPStatusError as e:
            logger.error(f"MCP 调用失败: {tool_name} -> {e}")
            return {"status": "error", "message": str(e)}

mcp_client = MCPClient()