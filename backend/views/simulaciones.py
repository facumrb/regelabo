"""
Endpoints de simulaciones. Pedir una devuelve 202 enseguida: la ejecuta el worker y el cliente
consulta el estado con GET (ver decisión 020).
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from backend.controller import simulaciones
from backend.controller.modelos import PaginaDeSimulaciones, Simulacion, SimulacionInput, Usuario
from backend.views.dependencias import usuario_actual

router = APIRouter(prefix="/simulaciones", tags=["Simulaciones"])


@router.post("", response_model=Simulacion, status_code=status.HTTP_202_ACCEPTED)
def crear(datos: SimulacionInput, usuario: Usuario = Depends(usuario_actual)) -> Simulacion:
    return simulaciones.crear(usuario, datos)


@router.get("", response_model=PaginaDeSimulaciones)
def listar(limite: int = Query(20, ge=1, le=100), despues_de: Optional[UUID] = None,
           caso_id: Optional[UUID] = None,
           usuario: Usuario = Depends(usuario_actual)) -> PaginaDeSimulaciones:
    return simulaciones.listar(usuario, caso_id, limite, despues_de)


@router.get("/{simulacion_id}", response_model=Simulacion)
def ver(simulacion_id: UUID, usuario: Usuario = Depends(usuario_actual)) -> Simulacion:
    return simulaciones.ver(usuario, simulacion_id)
