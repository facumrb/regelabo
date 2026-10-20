"""
Endpoints de casos de estudio. Todos requieren sesión; el controller se encarga de que
cada usuario vea solo los suyos.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from backend.controller import casos
from backend.controller.modelos import Caso, CasoInput, PaginaDeCasos, Usuario
from backend.views.dependencias import usuario_actual

router = APIRouter(prefix="/casos", tags=["Casos"])


@router.get("", response_model=PaginaDeCasos)
def listar(limite: int = Query(20, ge=1, le=100), despues_de: Optional[UUID] = None,
           usuario: Usuario = Depends(usuario_actual)) -> PaginaDeCasos:
    return casos.listar(usuario, limite, despues_de)


@router.post("", response_model=Caso, status_code=status.HTTP_201_CREATED)
def crear(datos: CasoInput, usuario: Usuario = Depends(usuario_actual)) -> Caso:
    return casos.crear(usuario, datos)


@router.get("/{caso_id}", response_model=Caso)
def ver(caso_id: UUID, usuario: Usuario = Depends(usuario_actual)) -> Caso:
    return casos.ver(usuario, caso_id)


@router.put("/{caso_id}", response_model=Caso)
def editar(caso_id: UUID, datos: CasoInput, usuario: Usuario = Depends(usuario_actual)) -> Caso:
    return casos.editar(usuario, caso_id, datos)


@router.delete("/{caso_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar(caso_id: UUID, usuario: Usuario = Depends(usuario_actual)) -> None:
    casos.borrar(usuario, caso_id)
