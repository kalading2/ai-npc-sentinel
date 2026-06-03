# AI NPC Sentinel

基于 LangGraph 的 3D 智能 NPC 系统 —— 让 NPC 从“脚本执行者”进化为“自主决策者”。

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 一、项目简介

AI NPC Sentinel 是一个面向企业级 3D 仿真与游戏场景的智能 NPC 后端系统。

**核心能力**：
- 🧠 **自主决策**：NPC 能根据环境感知，自主判断威胁等级并做出行为决策
- 📚 **知识驱动**：基于 RAG 技术，让 NPC 行为遵循策划编写的业务规则
- 🔧 **工具调用**：通过 MCP 协议，AI 可以直接操控 3D 引擎中的功能
- 🧠 **记忆系统**：短期 + 长期记忆，让 NPC 记住玩家行为和关键事件
- 🚀 **企业级架构**：三层解耦，支持私有化部署，模型可替换

**验证 Demo**：城堡守卫“阿托”——一个满嘴脏话、脾气火爆的老兵，能根据玩家行为自主决定盘查、警告、拉警报还是直接开打。

## 二、系统架构

```
┌─────────────────────────────────────────────────────────┐\
│ UE5 Client (C++) │\
│ ┌──────────┐ ┌──────────┐ ┌────────────────────────┐ │\
│ │ 感知组件 │ │ 行为执行 │ │ MCP Server (工具注册) │ │\
│ └────┬─────┘ └────▲─────┘ └────────▲───────────────┘ │\
│ │ HTTP │ HTTP │ MCP Protocol │\
└───────┼─────────────┼─────────────────┼───────────────────┘\
▼ │ │\
┌─────────────────────────────────────────────────────────┐\
│ LangGraph Agent (FastAPI + Python) │\
│ │\
│ ┌───────────────────────────────────────────────────┐ │\
│ │ StateGraph │ │\
│ │ \[意图识别] → \[知识检索] → \[威胁评估] → \[行动决策] │ │\
│ │ │ │ │ │ │ │\
│ │ ▼ ▼ ▼ ▼ │ │\
│ │ LangChain LlamaIndex LLM推理 工具调用 │ │\
│ │ Memory +ChromaDB (阿里百炼) (MCP) │ │\
│ └───────────────────────────────────────────────────┘ │\
│ │\
│ 对外接口: POST /decide | /decide/stream | /reset │\
└─────────────────────────────────────────────────────────┘

**三层解耦设计**：
- **表现层** (UE5)：负责 3D 渲染、感知采集、行为执行，不关心 AI 如何决策
- **编排层** (LangGraph Agent)：负责决策流程、记忆管理、工具调用编排
- **模型层** (阿里百炼)：提供 LLM 推理和 Embedding 能力，可替换
```

## 三、技术栈

| 层级 | 技术 | 作用 |
|:---|:---|:---|
| AI 编排 | LangGraph 0.2 | 状态图编排、决策流程管理 |
| LLM 集成 | LangChain 0.3 | Memory管理、Prompt模板 |
| 大模型 | 阿里百炼 qwen-turbo | 意图识别、威胁评估、对话生成 |
| 向量数据库 | ChromaDB | 知识库存储、语义检索 |
| 知识检索 | LlamaIndex | 文档索引、RAG |
| Embedding | DashScope text-embedding-v2 | 文本向量化 |
| 工具调用 | MCP Protocol | Agent 安全调用引擎内函数 |
| 后端框架 | FastAPI + Uvicorn | 异步 API 服务 |
| 通信协议 | HTTP + SSE | 请求响应 + 流式推送 |
| 项目管理 | uv + Python 3.12 | 现代 Python 工程管理 |

## 四、快速启动

### 4.1 环境要求

- Python 3.12+
- 阿里百炼 API Key ([申请地址](https://dashscope.console.aliyun.com/))
- (可选) UE5.4+ 用于 3D 端联调

### 4.2 安装 uv (推荐)

```bash
# Windows PowerShell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 4.3 克隆项目

```bash
    git clone https://github.com/你的用户名/ai-npc-sentinel.git
    cd ai-npc-sentinel
```

### 4.4 配置环境变量

```bash
    # 复制配置模板
    cp .env.example .env

    # 编辑 .env，填入你的阿里百炼 API Key
    OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
```

### 4.5 安装依赖

```bash
    uv sync
```

### 4.6 启动服务

```bash
    uv run uvicorn agent.main:app --reload --host 0.0.0.0 --port 8000
```

### 4.7 验证

```bash
    # 健康检查
    curl http://localhost:8000/health

    # 发送决策请求
    curl -X POST http://localhost:8000/decide \
      -H "Content-Type: application/json" \
      -d '{
        "npc_id": "guard_atto",
        "session_id": "test_001",
        "perception": {
          "player_distance": 150.0,
          "player_visible": true,
          "player_weapon_drawn": true,
          "time_of_day": "night"
        }
      }'
```

## 五、接口文档

### 5.1`POST /decide`

核心决策接口，接收感知数据，返回 NPC 行为。

### 5.2`POST /decide/stream`

SSE 流式接口，实时推送 NPC 对话 token。

### 5.3 `POST /reset/{npc_id}`

重置指定 NPC 的短期记忆。

### 5.4 GET /tools`

返回当前可用的工具列表。


## 六、项目结构
```
    ai-npc-sentinel/
    ├── agent/
    │   ├── main.py                 # FastAPI 入口
    │   ├── config.py               # 全局配置
    │   ├── api/
    │   │   ├── routes.py           # API 路由
    │   │   └── schemas.py          # 数据模型
    │   ├── graph/
    │   │   ├── state.py            # AgentState 定义
    │   │   ├── builder.py          # StateGraph 构建
    │   │   └── nodes/              # 各节点实现
    │   │       ├── intent_recognition.py
    │   │       ├── threat_assessment.py
    │   │       ├── knowledge_retrieval.py
    │   │       ├── tool_calling.py
    │   │       └── action_decision.py
    │   ├── llm/
    │   │   ├── llm_client.py       # LLM 调用封装
    │   │   └── prompt_templates.py # Prompt 模板
    │   ├── knowledge/
    │   │   ├── indexer.py          # 文档索引
    │   │   ├── retriever.py        # 知识检索
    │   │   └── documents/
    │   │       └── guard_rules.txt # 守卫守则
    │   ├── memory/
    │   │   ├── short_term.py       # 短期记忆
    │   │   └── long_term.py        # 长期记忆
    │   └── tools/
    │       ├── tool_registry.py    # 工具注册表
    │       └── mcp_client.py       # MCP 客户端
    ├── data/                       # 持久化数据
    ├── docs/                       # 文档
    ├── docker-compose.yml
    ├── pyproject.toml
    └── README.md
```

## 七、演示 Demo

### 7.1 暗号测试（验证知识库）

json
```
    {
      "npc_id": "guard_atto",
      "session_id": "test_knowledge",
      "perception": {
        "player_distance": 500.0,
        "player_visible": true,
        "player_weapon_drawn": false,
        "time_of_day": "day",
        "last_player_action": "玩家说：今天月亮真圆"
      }
    }
```
**预期回复**：`"土豆土豆，我是地瓜。"`

### 7.2 高威胁测试（验证工具调用）

json
```
    {
      "npc_id": "guard_atto",
      "session_id": "test_high_threat",
      "perception": {
        "player_distance": 50.0,
        "player_visible": true,
        "player_weapon_drawn": true,
        "time_of_day": "night"
      }
    }
```
**预期行为**：拉响警报 + 拔剑 + 骂人

## 八、性能

| 模型         | 端到端延迟  | 适用场景    |
| :--------- | :----- | :------ |
| qwen-turbo | \~3.4s | Demo 推荐 |
| qwen-plus  | \~7s   | 中等智能需求  |
| qwen-max   | \~43s  | 仅测试，不推荐 |

延迟包含：知识库检索 + 多节点 LLM 推理 + MCP 工具调用。

## 九、后续规划

*   多 NPC 协作 (Multi-Agent)

*   UE 端 MCP Server 完整实现

*   长期记忆 ChromaDB 持久化

*   Docker 一键部署

*   支持更多模型 (DeepSeek-V3, Qwen3)
