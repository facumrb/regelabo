"""
Comentarios y sugerencias (RN13): cualquier usuario con sesión deja uno. Verlos y marcarlos
es del panel de admin (`views/admin.py`).
"""

from fastapi import APIRouter, Depends, Request, status

from backend.controller import comentarios
from backend.controller.modelos import ComentarioInput, Usuario
from backend.views.dependencias import usuario_actual
from backend.views.limites import limiter, por_sesion

router = APIRouter(prefix="/comentarios", tags=["Comentarios"])


@router.post("", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute", key_func=por_sesion)  # contra el spam (decisión 028)
def crear(request: Request, datos: ComentarioInput, usuario: Usuario = Depends(usuario_actual)) -> None:
    comentarios.crear(usuario, datos)
