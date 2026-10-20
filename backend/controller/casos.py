"""
Casos de estudio: el módulo de ejemplo. Cada operación recibe el usuario de la sesión
y solo ve sus propios casos (RN4): un caso ajeno o borrado da `caso_no_encontrado` (404).
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from backend.controller.errores import ErrorDeNegocio
from backend.controller.modelos import Caso, CasoInput, PaginaDeCasos, Usuario
from backend.datos import casos
from backend.datos.conexion import transaccion

_NO_ENCONTRADO = ErrorDeNegocio("caso_no_encontrado", "El caso no existe.")


def crear(usuario: Usuario, datos: CasoInput) -> Caso:
    with transaccion() as tx:
        return casos.crear(tx, usuario.id, datos)


def listar(usuario: Usuario, limite: int, despues_de: Optional[UUID]) -> PaginaDeCasos:
    with transaccion() as tx:
        pagina = casos.listar(tx, usuario.id, limite + 1, despues_de)  # uno de más: dice si hay siguiente
    hay_mas = len(pagina) > limite
    pagina = pagina[:limite]
    return PaginaDeCasos(casos=pagina, siguiente=pagina[-1].id if hay_mas else None)


def ver(usuario: Usuario, caso_id: UUID) -> Caso:
    with transaccion() as tx:
        caso = casos.buscar(tx, caso_id, usuario.id)
    if caso is None:
        raise _NO_ENCONTRADO
    return caso


def editar(usuario: Usuario, caso_id: UUID, datos: CasoInput) -> Caso:
    with transaccion() as tx:
        caso = casos.actualizar(tx, caso_id, usuario.id, datos)
    if caso is None:
        raise _NO_ENCONTRADO
    return caso


def borrar(usuario: Usuario, caso_id: UUID) -> None:
    with transaccion() as tx:
        borrado = casos.borrar(tx, caso_id, usuario.id, datetime.now(timezone.utc))
    if not borrado:
        raise _NO_ENCONTRADO
