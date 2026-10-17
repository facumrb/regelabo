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
