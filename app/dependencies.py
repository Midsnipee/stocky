from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status

from .models import Role


def get_current_role(x_user_role: str | None = Header(default=None)) -> Role:
    if x_user_role is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-User-Role header")
    try:
        return Role(x_user_role)
    except ValueError as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role") from exc


def require_roles(*allowed: Role):
    def dependency(role: Role = Depends(get_current_role)) -> Role:
        if role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return role

    return dependency
