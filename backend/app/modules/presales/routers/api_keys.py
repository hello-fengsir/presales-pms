"""API Key 管理路由 — 支持国内主流大模型"""
import logging
import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...auth.router import get_current_user
from ..database import get_db
from ..models import ApiKey
from ..providers import PROVIDERS

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api-keys", tags=["API密钥"])


class ApiKeyCreate(BaseModel):
    provider: str
    model: str
    api_key: str
    base_url: str = ""


class ApiKeyOut(BaseModel):
    id: int
    provider: str
    model: str
    api_key: str  # 脱敏返回后4位
    base_url: str
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


class TestKeyRequest(BaseModel):
    provider: str
    model: str
    api_key: str
    base_url: str = ""


# ── Provider 列表 ──
@router.get("/providers")
def list_providers():
    """返回所有支持的服务商及模型列表"""
    result = []
    for key, cfg in PROVIDERS.items():
        result.append({
            "id": key,
            "name": cfg["name"],
            "models": cfg["models"],
        })
    return result


# ── 我的 Key 列表 ──
@router.get("", response_model=list[ApiKeyOut])
def list_keys(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(
        select(ApiKey).where(ApiKey.username == user["username"]).order_by(ApiKey.updated_at.desc())
    ).all()
    result = []
    for r in rows:
        mask = r.api_key[:4] + "****" + r.api_key[-4:] if len(r.api_key) > 8 else "****"
        result.append(ApiKeyOut(
            id=r.id, provider=r.provider, model=r.model,
            api_key=mask, base_url=r.base_url, is_active=r.is_active,
            created_at=r.created_at.isoformat() if r.created_at else "",
        ))
    return result


# ── 保存/更新 Key ──
@router.post("")
def save_key(data: ApiKeyCreate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """保存或更新 API Key（同一 provider+model 唯一）"""
    existing = db.scalars(
        select(ApiKey).where(
            ApiKey.username == user["username"],
            ApiKey.provider == data.provider,
            ApiKey.model == data.model,
        )
    ).first()

    base_url = data.base_url or PROVIDERS.get(data.provider, {}).get("base_url", "")

    if existing:
        existing.api_key = data.api_key
        existing.base_url = base_url
        existing.is_active = True
    else:
        new_key = ApiKey(
            username=user["username"],
            provider=data.provider,
            model=data.model,
            api_key=data.api_key,
            base_url=base_url,
            is_active=True,
        )
        db.add(new_key)
    db.commit()
    return {"ok": True}


# ── 删除 Key ──
@router.delete("/{key_id}")
def delete_key(key_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.scalars(
        select(ApiKey).where(ApiKey.id == key_id, ApiKey.username == user["username"])
    ).first()
    if not row:
        raise HTTPException(404, "Key 不存在")
    db.delete(row)
    db.commit()
    return {"ok": True}


# ── 测试 Key 有效性 ──
@router.post("/test")
async def test_key(data: TestKeyRequest):
    """测试 API Key 是否有效 — 发送最小请求验证连通性"""
    cfg = PROVIDERS.get(data.provider)
    if not cfg:
        raise HTTPException(400, f"不支持的服务商: {data.provider}")

    base = data.base_url or cfg["base_url"]
    url = base.rstrip("/") + cfg["api_path"]
    auth_value = cfg["auth_prefix"] + data.api_key
    test_body = cfg["test_body"](data.model)

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                url,
                headers={
                    "Content-Type": "application/json",
                    cfg["auth_header"]: auth_value,
                },
                json=test_body,
            )
        if resp.status_code == 200:
            result = resp.json()
            content = ""
            try:
                content = result["choices"][0]["message"]["content"]
            except (KeyError, IndexError):
                content = str(result)[:100]
            return {"ok": True, "status": resp.status_code, "preview": content.strip()}
        else:
            detail = ""
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text[:300]
            return {"ok": False, "status": resp.status_code, "detail": str(detail)}
    except httpx.TimeoutException:
        return {"ok": False, "status": 0, "detail": "连接超时（15秒），请检查网络或 base_url"}
    except httpx.ConnectError:
        return {"ok": False, "status": 0, "detail": "无法连接服务器，请检查 base_url 是否正确"}
    except Exception as e:
        return {"ok": False, "status": 0, "detail": str(e)[:500]}
