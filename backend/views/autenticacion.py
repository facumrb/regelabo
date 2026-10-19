"""
Endpoints de registro, inicio y cierre de sesión.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Request, Response, status

from backend.configuracion import COOKIE_SECURE, SESION_HORAS
from backend.controller import autenticacion
from backend.controller.modelos import (CambioContrasenaInput, LoginInput, RegistroInput, Usuario,
                                        UsuarioPublico)
from backend.views.dependencias import COOKIE_SESION, token_de_sesion, usuario_actual
from backend.views.limites import limiter

router = APIRouter(prefix="/auth", tags=["Autenticación"])

LIMITE_INTENTOS = "5/minute"


@router.post("/registro", response_model=UsuarioPublico, status_code=status.HTTP_201_CREATED)
@limiter.limit(LIMITE_INTENTOS)
def registro(request: Request, datos: RegistroInput) -> Usuario:
    return autenticacion.registrar(datos)


@router.post("/login", response_model=UsuarioPublico)
@limiter.limit(LIMITE_INTENTOS)
def login(request: Request, response: Response, datos: LoginInput) -> Usuario:
    token, usuario = autenticacion.iniciar_sesion(datos.email, datos.password)
    response.set_cookie(
        COOKIE_SESION, token, max_age=SESION_HORAS * 3600, path="/api",
        httponly=True, samesite="lax", secure=COOKIE_SECURE,
    )
    return usuario


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response, token: Optional[str] = Depends(token_de_sesion)) -> None:
    autenticacion.cerrar_sesion(token)
    response.delete_cookie(COOKIE_SESION, path="/api")


@router.post("/contrasena", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(LIMITE_INTENTOS)
def cambiar_contrasena(request: Request, datos: CambioContrasenaInput,
                       usuario: Usuario = Depends(usuario_actual),
                       token: Optional[str] = Depends(token_de_sesion)) -> None:
    autenticacion.cambiar_contrasena(usuario, token, datos.actual, datos.nueva)


@router.get("/yo", response_model=UsuarioPublico)
def yo(usuario: Usuario = Depends(usuario_actual)) -> Usuario:
    return usuario
