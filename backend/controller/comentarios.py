"""
Comentarios y sugerencias (RN13, decisión 028). Cualquier usuario con sesión deja uno y no
recibe estado ni respuesta; solo el admin los ve y los marca (la vista pide `requiere_admin`).
"""

from typing import Optional
from uuid import UUID

from backend.controller.errores import ErrorDeNegocio
from backend.controller.modelos import (Comentario, ComentarioInput, EstadoComentario, PaginaDeComentarios,
                                        TipoPerfil, Usuario)
from backend.datos import comentarios
from backend.datos.conexion import transaccion

# Sin filtro de estado, el admin ve lo que todavía no archivó
_SIN_ARCHIVAR = ["nuevo", "leido"]


def crear(usuario: Usuario, datos: ComentarioInput) -> None:
    with transaccion() as tx:
        comentarios.crear(tx, usuario.id, datos.texto)


def listar(limite: int, despues_de: Optional[UUID], estado: Optional[EstadoComentario],
           tipo: Optional[TipoPerfil]) -> PaginaDeComentarios:
    estados = [estado] if estado else _SIN_ARCHIVAR
    with transaccion() as tx:
        # uno de más: dice si hay página siguiente
        pagina = comentarios.listar(tx, limite + 1, despues_de, estados, tipo)
    hay_mas = len(pagina) > limite
    pagina = pagina[:limite]
    return PaginaDeComentarios(comentarios=pagina, siguiente=pagina[-1].id if hay_mas else None)


def cambiar_estado(comentario_id: UUID, estado: EstadoComentario) -> Comentario:
    """Cualquier estado a cualquier otro: así un clic por error se corrige solo."""
    with transaccion() as tx:
        comentario = comentarios.cambiar_estado(tx, comentario_id, estado)
    if comentario is None:
        raise ErrorDeNegocio("comentario_no_encontrado", "El comentario no existe.")
    return comentario
