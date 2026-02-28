from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud.user import create_user, get_user_by_username, login_user, get_current_user
from models.users import User
from schema.user import LoginRequest, RegisterRequest
from utils.security import verify_password


router = APIRouter(prefix="/user", tags=["用户"])

async def get_token_from_header(authorization: str = Header(...)):
    """从请求头中提取 token"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="无效的认证格式")
    return authorization[7:]

@router.post("/register")
async def register_user(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    user = await get_user_by_username(request.username, db)
    if user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    await create_user(request, db)
    return {"msg": "用户注册成功"}

@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    user = await login_user(request, db)
    if not user:
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    return {"msg": "登录成功", "token": user["token"]}

@router.get("/me")
async def get_current_user_info(
    token: str = Depends(get_token_from_header),
    db: AsyncSession = Depends(get_db)
):
    """获取当前用户信息"""
    current_user = await get_current_user(token, db)
    return {
        "id": current_user.id,
        "username": current_user.username
    }
