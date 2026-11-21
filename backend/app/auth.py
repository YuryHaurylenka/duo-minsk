from dataclasses import dataclass
from functools import lru_cache
from uuid import UUID
import json
import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import get_db


@dataclass(frozen=True)
class AuthUser:
    id: UUID
    email: str | None = None


bearer = HTTPBearer(auto_error=False)


@lru_cache
def _jwks_client(url: str) -> PyJWKClient:
    return PyJWKClient(f"{url.rstrip('/')}/auth/v1/.well-known/jwks.json", cache_keys=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> AuthUser:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Требуется авторизация")
    settings = get_settings()
    token = credentials.credentials
    try:
        header = jwt.get_unverified_header(token)
        algorithm = header.get("alg", "")
        issuer = f"{settings.supabase_url.rstrip('/')}/auth/v1"
        if algorithm == "HS256" and settings.supabase_jwt_secret:
            payload = jwt.decode(token, settings.supabase_jwt_secret, algorithms=["HS256"], audience="authenticated", issuer=issuer)
        else:
            signing_key = _jwks_client(settings.supabase_url).get_signing_key_from_jwt(token).key
            payload = jwt.decode(token, signing_key, algorithms=["ES256", "RS256"], audience="authenticated", issuer=issuer)
        user_id = UUID(payload["sub"])
        claims = {"sub": str(user_id), "role": "authenticated", "email": payload.get("email")}
        db.execute(text("RESET ROLE"))
        db.execute(text("SET LOCAL ROLE authenticated"))
        db.execute(text("SELECT set_config('request.jwt.claim.sub', :sub, true)"), {"sub": str(user_id)})
        db.execute(text("SELECT set_config('request.jwt.claims', :claims, true)"), {"claims": json.dumps(claims)})
        return AuthUser(id=user_id, email=payload.get("email"))
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительная или истёкшая сессия")


def require_user(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    return user


def require_match_user(
    user: AuthUser = Depends(require_user),
    db: Session = Depends(get_db),
) -> AuthUser:
    """Switch authenticated Match API requests to the backend-only database role."""
    db.execute(text("RESET ROLE"))
    db.execute(text("SET LOCAL ROLE duo_match_backend"))
    return user
