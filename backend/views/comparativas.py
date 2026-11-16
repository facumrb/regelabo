"""
Comparativas guardadas (decisión 025). Todas requieren sesión; el controller se encarga de que cada
usuario vea solo las suyas.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from backend.controller import comparativas
from backend.controller.modelos import (Comparativa, ComparativaDatos, ComparativaInput, PaginaDeComparativas,
                                        Usuario)
from backend.views.dependencias import usuario_actual

router = APIRouter(prefix="/comparativas", tags=["Comparativas"])


@router.get("", response_model=PaginaDeComparativas)
def listar(limite: int = Query(20, ge=1, le=100), despues_de: Optional[UUID] = None,
           caso_id: Optional[UUID] = Query(None, description="Solo las de este caso"),
           usuario: Usuario = Depends(usuario_actual)) -> PaginaDeComparativas:
    return comparativas.listar(usuario, limite, despues_de, caso_id)


@router.post("", response_model=Comparativa, status_code=status.HTTP_201_CREATED)
def crear(datos: ComparativaInput, usuario: Usuario = Depends(usuario_actual)) -> Comparativa:
    return comparativas.crear(usuario, datos)


@router.get("/{comparativa_id}", response_model=Comparativa)
def ver(comparativa_id: UUID, usuario: Usuario = Depends(usuario_actual)) -> Comparativa:
    return comparativas.ver(usuario, comparativa_id)


@router.put("/{comparativa_id}", response_model=Comparativa)
def editar(comparativa_id: UUID, datos: ComparativaDatos,
           usuario: Usuario = Depends(usuario_actual)) -> Comparativa:
    return comparativas.editar(usuario, comparativa_id, datos)


@router.delete("/{comparativa_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar(comparativa_id: UUID, usuario: Usuario = Depends(usuario_actual)) -> None:
    comparativas.borrar(usuario, comparativa_id)
