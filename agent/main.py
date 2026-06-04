# agent/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agent.api.routes import router as agent_router
from loguru import logger
from pathlib import Path
import sys
from dotenv import load_dotenv
import uvicorn

def app_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent

load_dotenv(app_dir() / ".env")

# 创建 FastAPI 应用实例
app = FastAPI(
    title="AI NPC Sentinel",
    description="3D AI NPC 智能哨兵 - LangGraph Agent 服务",
    version="1.0",
)

# 配置 CORS，允许 UE5 客户端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 路由定义
# ==========================================
app.include_router(agent_router)

@app.get("/")
async def root():
    logger.info("AI NPC Sentinel Agent 服务启动中...")
    return {"message": "AI NPC Sentinel Agent 服务运行中"}

@app.get("/health")
async def health():
    """健康检查接口"""
    logger.info("Health check called")
    return {"status": "ok"}

# ==========================================
# 启动入口
# ==========================================

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)

