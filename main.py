from contextlib import asynccontextmanager
from fastapi import FastAPI
from config.db_conf import init_db
from routers import report
from models.users import User, Token
from routers import user



@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    await init_db()
    print("✅ 数据库初始化完成")
    yield
    print("👋 应用关闭")

# 初始化 FastAPI 应用
app = FastAPI(lifespan=lifespan)

app.include_router(report.router)
app.include_router(user.router)



