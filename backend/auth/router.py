import sqlite3
from fastapi import APIRouter, Depends, Header, HTTPException

from auth.schemas import LoginRequest, RegisterRequest
from auth.service import authenticate_user, create_session, create_user, get_user_by_token, init_auth_db, revoke_session

router = APIRouter(prefix="/api/auth", tags=["账户认证"])
init_auth_db()

def current_token(authorization: str | None = Header(default=None)):
    if not authorization: raise HTTPException(status_code=401, detail="请先登录")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip(): raise HTTPException(status_code=401, detail="登录凭证无效")
    return token.strip()

def current_user(token: str = Depends(current_token)):
    user = get_user_by_token(token)
    if not user: raise HTTPException(status_code=401, detail="登录已失效，请重新登录")
    return user

@router.post("/register")
def register(data: RegisterRequest):
    try: user = create_user(data.email, data.password)
    except sqlite3.IntegrityError as exc: raise HTTPException(status_code=409, detail="该邮箱已注册") from exc
    return {"success": True, "message": "注册成功", "user": user}

@router.post("/login")
def login(data: LoginRequest):
    user = authenticate_user(data.email, data.password)
    if not user: raise HTTPException(status_code=401, detail="邮箱或密码错误")
    token, expires_at = create_session(user["id"])
    return {"success": True, "message": "登录成功", "access_token": token, "token_type": "Bearer", "expires_at": expires_at, "user": user}

@router.get("/me")
def me(user: dict = Depends(current_user)): return {"success": True, "user": user}

@router.post("/logout")
def logout(token: str = Depends(current_token)):
    revoke_session(token)
    return {"success": True, "message": "已退出登录"}
