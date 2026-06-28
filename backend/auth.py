"""
管理员认证 — 基于 HMAC 签名的简单 Token
密码从 config.json 文件读取，修改后无需重启
"""

import hashlib
import hmac
import json
import os
import time
from pathlib import Path
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# 配置文件路径（与 auth.py 同目录）
CONFIG_FILE = Path(__file__).parent / "config.json"
SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(32).hex())

security = HTTPBearer(auto_error=False)

# 缓存：上次读取的 mtime 和密码
_cache = {"mtime": 0, "password": ""}


def _load_config() -> dict:
    """加载配置文件，文件不存在时自动创建"""
    if not CONFIG_FILE.exists():
        default = {"admin_password": "changeme"}
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
        return default
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_admin_password() -> str:
    """
    获取管理员密码。
    优先从环境变量读取，否则从 config.json 读取（带 mtime 缓存）。
    """
    env_pass = os.environ.get("ADMIN_PASSWORD", "")
    if env_pass:
        return env_pass

    mtime = CONFIG_FILE.stat().st_mtime if CONFIG_FILE.exists() else 0
    if mtime != _cache["mtime"]:
        config = _load_config()
        _cache["mtime"] = mtime
        _cache["password"] = config.get("admin_password", "")
    return _cache["password"]


def _sign(payload: str) -> str:
    """对 payload 进行 HMAC-SHA256 签名"""
    sig = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{sig}"


def _verify(token: str) -> bool:
    """验证 token 签名"""
    try:
        payload, sig = token.rsplit(".", 1)
        expected = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return False
        # 检查过期时间（24 小时）
        ts = int(payload.split(":")[1])
        if time.time() - ts > 86400:
            return False
        return True
    except Exception:
        return False


def verify_password(password: str) -> str | None:
    """验证密码，成功返回 token"""
    admin_password = get_admin_password()
    if not admin_password:
        return None
    if password == admin_password:
        payload = f"admin:{int(time.time())}"
        return _sign(payload)
    return None


def require_auth(credentials: HTTPAuthorizationCredentials | None = Depends(security)):
    """FastAPI 依赖：检查请求是否携带有效 token"""
    admin_password = get_admin_password()
    if not admin_password:
        # 未设置密码则跳过认证
        return True

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    if not _verify(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录已过期，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return True
