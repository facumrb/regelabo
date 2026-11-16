"""
Panel de administración (decisión 028): todo bajo /api/admin y solo para admin.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from backend.controller import comentarios, simulaciones, usuarios
from backend.controller.modelos import (CambioEstadoComentario, Comentario, ContrasenaTemporal, EstadoCola,
                                        EstadoComentario, PaginaDeComentarios, PaginaDeUsuarios, Pendientes,
                                        TipoPerfil, UsuarioAdmin)
from backend.views.dependencias import requiere_admin

router = APIRouter(prefix="/admin", tags=["Administración"], dependencies=[Depends(requiere_admin)])


@router.get("/pendientes", response_model=Pendientes)
def pendientes() -> Pendientes:
    return usuarios.pendientes()


@router.get("/comentarios", response_model=PaginaDeComentarios)
def listar_comentarios(limite: int = Query(20, ge=1, le=100),
                       despues_de: Optional[UUID] = None,
                       estado: Optional[EstadoComentario] = Query(None, description="Sin él: no archivados"),
                       tipo: Optional[TipoPerfil] = None) -> PaginaDeComentarios:
    return comentarios.listar(limite, despues_de, estado, tipo)


@router.patch("/comentarios/{comentario_id}", response_model=Comentario)
def cambiar_estado(comentario_id: UUID, datos: CambioEstadoComentario) -> Comentario:
    return comentarios.cambiar_estado(comentario_id, datos.estado)


@router.get("/usuarios", response_model=PaginaDeUsuarios)
def listar_usuarios(limite: int = Query(20, ge=1, le=100), despues_de: Optional[UUID] = None,
                    busqueda: Optional[str] = Query(None, max_length=254, description="Email o nombre"),
                    tipo: Optional[TipoPerfil] = None,
                    con_pedido: bool = Query(False, description="Solo los que pidieron restablecer")
                    ) -> PaginaDeUsuarios:
    return usuarios.listar(limite, despues_de, busqueda, tipo, con_pedido)


@router.post("/usuarios/{usuario_id}/desbloquear", response_model=UsuarioAdmin)
def desbloquear(usuario_id: UUID) -> UsuarioAdmin:
    return usuarios.desbloquear(usuario_id)


@router.post("/usuarios/{usuario_id}/verificar-email", response_model=UsuarioAdmin)
def verificar_email(usuario_id: UUID) -> UsuarioAdmin:
    return usuarios.verificar_email(usuario_id)


@router.post("/usuarios/{usuario_id}/resetear-contrasena", response_model=ContrasenaTemporal)
def resetear_contrasena(usuario_id: UUID) -> ContrasenaTemporal:
    return usuarios.resetear_contrasena(usuario_id)


@router.get("/cola", response_model=EstadoCola)
def estado_de_la_cola() -> EstadoCola:
    return simulaciones.estado_de_la_cola()
