import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User, Token
from schema.user import LoginRequest, RegisterRequest
from utils.security import hash_password, verify_password


async def get_user_by_username(username: str, db: AsyncSession):
    """根据用户名查询用户"""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()

async def create_user(request: RegisterRequest, db: AsyncSession):
    """创建用户"""
    password = hash_password(request.password)
    new_user = User(
    username=request.username,
    password=password  
    )
    db.add(new_user)
    await db.commit()
    return {"msg": "用户注册成功"}

async def login_user(request: LoginRequest, db: AsyncSession):
    """用户登录"""
    user = await get_user_by_username(request.username, db)
    if not user:
        raise HTTPException(status_code=400, detail="用户名不存在")
    if not verify_password(request.password, user.password):
        raise HTTPException(status_code=400, detail="密码错误")
    
    token = uuid.uuid4().hex
    expires_at = datetime.now() + timedelta(days=7)
    
    new_token = Token(
        token=token,
        user_id=user.id,
        expires_at=expires_at
    )
    
    db.add(new_token)
    await db.commit()
    
    return {"msg": "登录成功", "token": token}

async def get_current_user(token: str, db: AsyncSession):
    """根据token获取当前用户"""
    result = await db.execute(select(Token).where(Token.token == token))
    token_obj = result.scalar_one_or_none()
    if not token_obj:
        raise HTTPException(status_code=401, detail="token不存在")
    if token_obj.expires_at < datetime.now():
        raise HTTPException(status_code=401, detail="token已过期")
    result = await db.execute(select(User).where(User.id == token_obj.user_id))
    token_obj.expires_at = datetime.now() + timedelta(days=7)
    await db.commit()
    return result.scalar_one_or_none()
