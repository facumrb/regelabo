"""
Límite de pedidos por IP. Los contadores viven en memoria: si algún día hay varias
instancias de la API, hay que pasarlos a Redis.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)


def demasiados_pedidos(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": {"codigo": "demasiados_pedidos",
                            "mensaje": "Demasiados pedidos. Esperá un momento y reintentá."}},
    )


def por_sesion(request: Request) -> str:
    """Clave para límites por usuario: el token de la cookie (sin sesión, la IP)."""
    # shortcut: cuenta por sesión, no por usuario; con varias sesiones abiertas el tope se multiplica
    return request.cookies.get("sesion") or get_remote_address(request)
