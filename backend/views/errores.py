"""
Traducción de los errores de negocio a respuestas HTTP: {"detail": {"codigo": ..., "mensaje": ...}}.
"""

from fastapi import Request
from fastapi.responses import JSONResponse

from backend.controller.errores import ErrorDeNegocio

ESTADOS = {
    "no_autenticado": 401,
    "credenciales_invalidas": 401,
    "sin_permiso": 403,
    "usuario_no_encontrado": 404,
    "caso_no_encontrado": 404,  # también para casos ajenos (RN4): no revela que existen
    "email_ya_registrado": 409,
    "cuenta_bloqueada": 429,
    "cupo_agotado": 429,
    "limite_por_hora": 429,
    "sistema_saturado": 503,
    "simulacion_no_encontrada": 404,
    "estados_internos_no_disponibles": 404,
    "perfil_no_encontrado": 404,
}
ESTADO_POR_DEFECTO = 400


def manejar_error_de_negocio(request: Request, exc: ErrorDeNegocio) -> JSONResponse:
    return JSONResponse(
        status_code=ESTADOS.get(exc.codigo, ESTADO_POR_DEFECTO),
        content={"detail": {"codigo": exc.codigo, "mensaje": exc.mensaje}},
    )
