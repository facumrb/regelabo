"""
Límites de pedidos (slowapi). Los contadores viven en memoria: si algún día hay varias
instancias de la API, hay que pasarlos a Redis.

- Toda la API: 120 por minuto por sesión (decisión 009), con la dependencia global `limite_general`.
  No se usa `SlowAPIMiddleware`: con FastAPI 0.143 no encuentra las rutas de los routers
  (`_IncludedRouter`) y las deja pasar sin límite.
- Login, registro y demás de autenticación: además, 5 por minuto por IP (`por_ip`, en cada ruta).
"""

from fastapi import Request
from limits import parse
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from backend.controller.errores import ErrorDeNegocio

LIMITE_GENERAL = parse("120/minute")
EXENTAS = {"/api/health"}  # la consultan el chequeo del servidor y el chip del backend

por_ip = get_remote_address


def por_sesion(request: Request) -> str:
    """Clave para límites por usuario: el token de la cookie (sin sesión, la IP)."""
    # shortcut: cuenta por sesión, no por usuario; con varias sesiones abiertas el tope se multiplica
    return request.cookies.get("sesion") or get_remote_address(request)


limiter = Limiter(key_func=por_ip)


def limite_general(request: Request) -> None:
    """Dependencia de toda la app: usa los mismos contadores que slowapi (y su `enabled` y `reset`)."""
    if not limiter.enabled or request.url.path in EXENTAS:
        return
    if not limiter.limiter.hit(LIMITE_GENERAL, "general", por_sesion(request)):
        raise ErrorDeNegocio("demasiados_pedidos", "Demasiados pedidos. Esperá un momento y reintentá.")


def demasiados_pedidos(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": {"codigo": "demasiados_pedidos",
                            "mensaje": "Demasiados pedidos. Esperá un momento y reintentá."}},
    )
