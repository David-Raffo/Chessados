import secrets
import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from .config import DEFAULT_JWT_SECRET, JWT_DAYS, JWT_SECRET
from .db import SessionLocal, get_db
from .models import AppSetting, User

bearer = HTTPBearer(auto_error=False)

_secret: str | None = None


def jwt_secret() -> str:
    """Secreto para firmar los tokens. Nunca se usa el valor de ejemplo: si no hay JWT_SECRET propio en el
    .env, se genera uno aleatorio la primera vez y se guarda en la base de datos."""
    global _secret
    if _secret is None:
        if JWT_SECRET and JWT_SECRET != DEFAULT_JWT_SECRET:
            _secret = JWT_SECRET
        else:
            with SessionLocal() as db, db.begin():
                db.execute(insert(AppSetting).values(key="jwt_secret", value=secrets.token_hex(48))
                           .on_conflict_do_nothing(index_elements=["key"]))
            with SessionLocal() as db:
                _secret = db.scalar(select(AppSetting.value).where(AppSetting.key == "jwt_secret"))
    return _secret


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_token(user_id: int) -> str:
    exp = datetime.now(timezone.utc) + timedelta(days=JWT_DAYS)
    return jwt.encode({"sub": str(user_id), "exp": exp}, jwt_secret(), algorithm="HS256")


def current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)
) -> User:
    if creds is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "No autenticado")
    try:
        payload = jwt.decode(creds.credentials, jwt_secret(), algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sesión caducada")
    user = db.get(User, int(payload["sub"]))
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario no encontrado")
    return user


# --- Límite de intentos de inicio de sesión ---------------------------------------
# Por usuario (no por IP: detrás de lighttpd y nginx la IP del cliente se puede falsear).

MAX_FAILURES = 10
WINDOW = 15 * 60
_failures: dict[str, deque] = defaultdict(deque)
_lock = threading.Lock()


def check_login_allowed(username: str) -> None:
    now = time.monotonic()
    with _lock:
        q = _failures[username]
        while q and now - q[0] > WINDOW:
            q.popleft()
        if len(q) >= MAX_FAILURES:
            wait = int((WINDOW - (now - q[0])) / 60) + 1
            raise HTTPException(429, f"Demasiados intentos fallidos. Espera {wait} min y vuelve a probar.")


def register_login_failure(username: str) -> None:
    with _lock:
        _failures[username].append(time.monotonic())


def clear_login_failures(username: str) -> None:
    with _lock:
        _failures.pop(username, None)
