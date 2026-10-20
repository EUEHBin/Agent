import uuid
from datetime import datetime, timedelta, timezone

import jwt


def create_token(
    data: dict,
    secret_key: str,
    *,
    expires_delta: timedelta | None = None,
) -> str:
    payload = data.copy()
    if "sub" in payload and not isinstance(payload["sub"], str):
        payload["sub"] = str(payload["sub"])
    now = datetime.now(timezone.utc)
    payload.update(
        {
            "jti": str(uuid.uuid4()),
            "iat": now,
            "exp": now + (expires_delta or timedelta(hours=2)),
        }
    )
    return jwt.encode(payload, secret_key, algorithm="HS256")


def decode_token(
    token: str,
    secret_key: str,
) -> dict:
    return jwt.decode(
        token,
        secret_key,
        algorithms=["HS256"],
    )
