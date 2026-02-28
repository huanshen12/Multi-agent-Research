from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str  = Field(..., min_length=8, max_length=20, description="用户名")
    password: str  = Field(..., min_length=6, max_length=20, description="密码")

class LoginRequest(BaseModel):
    username: str  = Field(..., min_length=8, max_length=20, description="用户名")
    password: str  = Field(..., min_length=6, max_length=20, description="密码")