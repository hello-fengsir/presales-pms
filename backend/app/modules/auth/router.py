import json
import os
import bcrypt
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import JWTError, jwt

from app.config import settings

router = APIRouter()
security = HTTPBearer()

CRED_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "credentials.json")
SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
EXPIRE_MINUTES = settings.access_token_expire_minutes
DEFAULT_USERNAME = settings.admin_username
DEFAULT_PASSWORD = settings.admin_password


def _ensure_cred_file():
    os.makedirs(os.path.dirname(CRED_FILE), exist_ok=True)
    if not os.path.exists(CRED_FILE):
        pwd_hash = bcrypt.hashpw(DEFAULT_PASSWORD.encode(), bcrypt.gensalt()).decode()
        data = {
            "users": [{
                "username": DEFAULT_USERNAME,
                "password_hash": pwd_hash,
                "role": "admin",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }],
            "admin_index": 0,
        }
        with open(CRED_FILE, "w") as f:
            json.dump(data, f, indent=2)
    with open(CRED_FILE) as f:
        return json.load(f)


def _write_creds(data):
    with open(CRED_FILE, "w") as f:
        json.dump(data, f, indent=2)


class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class ChangeUsernameRequest(BaseModel):
    new_username: str
    password: str


def create_access_token(username: str, role: str = "admin"):
    expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINUTES)
    payload = {"sub": username, "role": role, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(401, "无效的认证令牌")
        return {"username": username, "role": payload.get("role", "admin")}
    except JWTError:
        raise HTTPException(401, "无效的认证令牌")


@router.post("/login")
def login(data: LoginRequest):
    creds = _ensure_cred_file()
    for user in creds["users"]:
        if user["username"] == data.username:
            if bcrypt.checkpw(data.password.encode(), user["password_hash"].encode()):
                token = create_access_token(user["username"], user.get("role", "admin"))
                return {"access_token": token, "token_type": "bearer", "username": user["username"]}
    raise HTTPException(401, "用户名或密码错误")


@router.put("/password")
def change_password(data: ChangePasswordRequest, user: dict = Depends(get_current_user)):
    creds = _ensure_cred_file()
    username = user["username"]
    for u in creds["users"]:
        if u["username"] == username:
            if not bcrypt.checkpw(data.old_password.encode(), u["password_hash"].encode()):
                raise HTTPException(400, "原密码错误")
            u["password_hash"] = bcrypt.hashpw(data.new_password.encode(), bcrypt.gensalt()).decode()
            _write_creds(creds)
            return {"ok": True}
    raise HTTPException(404, "用户不存在")


@router.put("/username")
def change_username(data: ChangeUsernameRequest, user: dict = Depends(get_current_user)):
    creds = _ensure_cred_file()
    old_username = user["username"]
    for u in creds["users"]:
        if u["username"] == data.new_username:
            raise HTTPException(400, "用户名已存在")
    for u in creds["users"]:
        if u["username"] == old_username:
            if not bcrypt.checkpw(data.password.encode(), u["password_hash"].encode()):
                raise HTTPException(400, "密码错误")
            u["username"] = data.new_username
            _write_creds(creds)
            token = create_access_token(data.new_username, u.get("role", "admin"))
            return {"access_token": token, "token_type": "bearer", "username": data.new_username}
    raise HTTPException(404, "用户不存在")
