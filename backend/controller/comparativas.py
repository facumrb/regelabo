"""
Comparativas guardadas (decisión 025): una superposición de 2 a 4 simulaciones propias y terminadas,
con título, notas y un caso opcional. Copia la estructura de Casos: cada usuario ve solo las suyas (RN4).
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from backend.controller.errores import ErrorDeNegocio
from backend.controller.modelos import (Comparativa, ComparativaDatos, ComparativaInput, PaginaDeComparativas,
                                        Usuario)
from backend.datos import casos, comparativas, simulaciones
from backend.datos.conexion import transaccion

_NO_ENCONTRADA = ErrorDeNegocio("comparativa_no_encontrada", "La comparativa no existe.")


def _validar_caso(tx, usuario: Usuario, caso_id: Optional[UUID]) -> None:
    if caso_id is not None and casos.buscar(tx, caso_id, usuario.id) is None:
        raise ErrorDeNegocio("caso_no_encontrado", "El caso no existe.")


def crear(usuario: Usuario, datos: ComparativaInput) -> Comparativa:
    if len(set(datos.simulacion_ids)) != len(datos.simulacion_ids):
        raise ErrorDeNegocio("simulaciones_repetidas", "Cada simulación va una sola vez en la comparativa.")
    with transaccion() as tx:
        _validar_caso(tx, usuario, datos.caso_id)
        estados = simulaciones.estados_propios(tx, datos.simulacion_ids, usuario.id)
        if len(estados) != len(datos.simulacion_ids):
            raise ErrorDeNegocio("simulacion_no_encontrada", "La simulación no existe.")  # ajena: como RN4
        if any(e != "completada" for e in estados.values()):
            raise ErrorDeNegocio("simulacion_sin_terminar", "Solo se pueden guardar simulaciones terminadas.")
        return comparativas.crear(tx, usuario.id, datos)


def listar(usuario: Usuario, limite: int, despues_de: Optional[UUID],
           caso_id: Optional[UUID]) -> PaginaDeComparativas:
    with transaccion() as tx:
        # uno de más: dice si hay página siguiente
        pagina = comparativas.listar(tx, usuario.id, limite + 1, despues_de, caso_id)
    hay_mas = len(pagina) > limite
    pagina = pagina[:limite]
    return PaginaDeComparativas(comparativas=pagina, siguiente=pagina[-1].id if hay_mas else None)


def ver(usuario: Usuario, comparativa_id: UUID) -> Comparativa:
    with transaccion() as tx:
        comparativa = comparativas.buscar(tx, comparativa_id, usuario.id)
    if comparativa is None:
        raise _NO_ENCONTRADA
    return comparativa


def editar(usuario: Usuario, comparativa_id: UUID, datos: ComparativaDatos) -> Comparativa:
    with transaccion() as tx:
        _validar_caso(tx, usuario, datos.caso_id)
        comparativa = comparativas.actualizar(tx, comparativa_id, usuario.id, datos)
    if comparativa is None:
        raise _NO_ENCONTRADA
    return comparativa


def borrar(usuario: Usuario, comparativa_id: UUID) -> None:
    with transaccion() as tx:
        borrada = comparativas.borrar(tx, comparativa_id, usuario.id, datetime.now(timezone.utc))
    if not borrada:
        raise _NO_ENCONTRADA
