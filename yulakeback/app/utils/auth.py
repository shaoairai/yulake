"""
JWT 認證工具
"""
import jwt
import os
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, g
from app.utils.errors import ApiError, ErrorCode

# JWT 設定
JWT_SECRET = os.getenv('JWT_SECRET', 'yulake-dev-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24 * 7  # 7 天


def create_token(payload: dict, expires_hours: int = JWT_EXPIRATION_HOURS) -> str:
    """
    建立 JWT Token

    Args:
        payload: Token 內容 (如 user_id, type)
        expires_hours: 過期時間（小時）

    Returns:
        str: JWT Token
    """
    now = datetime.now(timezone.utc)
    token_payload = {
        **payload,
        'iat': now,
        'exp': now + timedelta(hours=expires_hours)
    }
    return jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    """
    驗證 JWT Token

    Args:
        token: JWT Token

    Returns:
        dict: Token payload

    Raises:
        ApiError: Token 無效或過期
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ApiError(ErrorCode.AUTH_TOKEN_EXPIRED)
    except jwt.InvalidTokenError:
        raise ApiError(ErrorCode.AUTH_TOKEN_INVALID)


def get_token_from_header() -> str:
    """
    從 Authorization header 取得 Token

    Returns:
        str: Token (不含 Bearer 前綴)

    Raises:
        ApiError: 缺少或格式錯誤的 Authorization header
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise ApiError(ErrorCode.AUTH_REQUIRED)

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        raise ApiError(ErrorCode.AUTH_TOKEN_INVALID, 'Authorization header 格式錯誤')

    return parts[1]


def token_required(f):
    """
    需要有效 Token 的裝飾器

    驗證成功後，將 token payload 存入 g.token_payload
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        payload = verify_token(token)
        g.token_payload = payload
        return f(*args, **kwargs)
    return decorated


def salon_required(f):
    """
    需要店家身份的裝飾器

    驗證成功後：
    - g.token_payload: Token 內容
    - g.salon_id: 店家 ID
    - g.owner_id: 管理員 ID
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        payload = verify_token(token)

        if payload.get('type') != 'salon':
            raise ApiError(ErrorCode.AUTH_UNAUTHORIZED, '需要店家權限')

        g.token_payload = payload
        g.salon_id = payload.get('salon_id')
        g.owner_id = payload.get('owner_id')
        return f(*args, **kwargs)
    return decorated


def customer_required(f):
    """
    需要顧客身份的裝飾器

    驗證成功後：
    - g.token_payload: Token 內容
    - g.customer_id: 顧客 ID
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        payload = verify_token(token)

        if payload.get('type') != 'customer':
            raise ApiError(ErrorCode.AUTH_UNAUTHORIZED, '需要顧客權限')

        g.token_payload = payload
        g.customer_id = payload.get('customer_id')
        return f(*args, **kwargs)
    return decorated
