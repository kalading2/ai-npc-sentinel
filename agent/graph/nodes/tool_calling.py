from agent.graph.state import AgentState
from agent.llm.llm_client import llm_client
from agent.tools.mcp_client import mcp_client
from agent.tools.tool_registry import tool_registry

async def tool_calling(state: AgentState) -> dict:
    threat = state.get("threat_level","low")
    intent = state.get("intent","chat")
    perception = state.get("perception_json",{})

    # 1. 获取 OpenAI 标准格式工具列表，并绑定到模型
    tools = tool_registry.get_tools_openai_format()
    model_with_tools = llm_client.model.bind_tools(tools)

    # 2. 构造消息并调用 LLM
    system_prompt = f"威胁等级：{threat},意图：{intent}，感知：{perception}"
    from langchain_core.messages import SystemMessage
    messages = [SystemMessage(content=system_prompt)]
    response = await model_with_tools.ainvoke(messages)

    # 3. 解析并执行工具调用
    tool_calls = []
    tool_results = []
    for tool_call in response.tool_calls:
        tool_name = tool_call.get("name", "")
        args = tool_call.get("args", [])
        response = await mcp_client.call_tool(tool_name, args)
        tool_calls.append({"tool": tool_name, "args": args, "result": response})
        tool_results.append(str(response))

    return {
        "tool_calls": tool_calls,
        "tool_results": tool_results,
    }
