"""
Acceso a las simulaciones y a sus resultados. Todas las consultas de usuario filtran por dueño (RN4).
Las funciones reciben la sesión de `transaccion()` y devuelven objetos de negocio.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert  # ON CONFLICT: solo PostgreSQL
from sqlalchemy.orm import Session

from backend.controller.modelos import (
    ABRWavesData, EstadosInternos, HarmonicPeak, ParametrosSimulacion, SimulationResponse, Simulacion,
    SpectrumData,
)
from backend.datos.tablas import EstadosInternos as EstadosInternosFila
from backend.datos.tablas import ResultadoSimulacion as ResultadoFila
from backend.datos.tablas import Simulacion as SimulacionFila


def _parametros(fila: SimulacionFila) -> ParametrosSimulacion:
    return ParametrosSimulacion(
        carrier_freq=fila.frecuencia_portadora_hz, poles_profile=fila.perfil, spl_level=fila.nivel_db_spl,
        f_mod=fila.frecuencia_modulacion_hz, nH=fila.n_h, nM=fila.n_m, nL=fila.n_l,
    )


def _resultado(fila: ResultadoFila, parametros: ParametrosSimulacion) -> SimulationResponse:
    return SimulationResponse(
        execution_time_seconds=fila.duracion_s,
        efr_value_uv=fila.efr_uv,
        harmonics=[HarmonicPeak(**h) for h in fila.armonicos],
        fft_spectrum=SpectrumData(**fila.espectro),
        abr_waves=ABRWavesData(**fila.ondas),
        parameters_used=parametros.model_dump(),
    )


def _a_negocio(tx: Session, fila: SimulacionFila, con_detalle: bool) -> Simulacion:
    """Con `con_detalle`: incluye el resultado (si terminó) y la posición en la cola (si espera)."""
    parametros = _parametros(fila)
    resultado = None
    posicion = None
    if con_detalle and fila.resultado_id:
        resultado = _resultado(tx.get(ResultadoFila, fila.resultado_id), parametros)
    if con_detalle and fila.estado == "en_cola":
        posicion = tx.scalar(
            select(func.count()).where(SimulacionFila.estado == "en_cola", SimulacionFila.id <= fila.id)
        )
    return Simulacion(
        id=fila.id, estado=fila.estado, caso_id=fila.caso_id, parametros=parametros, creado_en=fila.creado_en,
        iniciada_en=fila.iniciada_en, finalizada_en=fila.finalizada_en, mensaje_error=fila.mensaje_error,
        # Un resultado reutilizado nunca llegó a ejecutarse
        reutilizada=fila.estado == "completada" and fila.iniciada_en is None,
        posicion=posicion, resultado=resultado, huella=fila.huella,
    )


def buscar_resultado_id(tx: Session, huella: str) -> Optional[UUID]:
    return tx.scalar(select(ResultadoFila.id).where(ResultadoFila.huella == huella))


def guardar_resultado(tx: Session, huella: str, resp: SimulationResponse) -> UUID:
    """Guarda el resultado; si otra simulación con la misma huella lo guardó antes, devuelve ese."""
    resultado_id = tx.scalar(
        insert(ResultadoFila).values(
            huella=huella, efr_uv=resp.efr_value_uv, armonicos=[h.model_dump() for h in resp.harmonics],
            espectro=resp.fft_spectrum.model_dump(), ondas=resp.abr_waves.model_dump(),
            metricas={}, duracion_s=resp.execution_time_seconds,
        ).on_conflict_do_nothing(index_elements=["huella"]).returning(ResultadoFila.id)
    )
    if resultado_id is None:
        return buscar_resultado_id(tx, huella)
    if resp.estados_internos is not None:
        tx.add(EstadosInternosFila(resultado_id=resultado_id, datos=resp.estados_internos.model_dump()))
    return resultado_id


def crear(tx: Session, usuario_id: UUID, caso_id: Optional[UUID], parametros: ParametrosSimulacion,
          huella: str, resultado_id: Optional[UUID], ahora: datetime) -> UUID:
    """Con `resultado_id` la simulación nace completada (caché); si no, queda en cola."""
    fila = SimulacionFila(
        usuario_id=usuario_id, caso_id=caso_id, perfil=parametros.poles_profile,
        frecuencia_portadora_hz=parametros.carrier_freq, nivel_db_spl=parametros.spl_level,
        frecuencia_modulacion_hz=parametros.f_mod, n_h=parametros.nH, n_m=parametros.nM, n_l=parametros.nL,
        huella=huella, estado="completada" if resultado_id else "en_cola", resultado_id=resultado_id,
        finalizada_en=ahora if resultado_id else None,
    )
    tx.add(fila)
    tx.flush()
    return fila.id


def contar_activas(tx: Session, usuario_id: UUID) -> int:
    """Simulaciones del usuario en cola o ejecutando (RN5a)."""
    return tx.scalar(select(func.count()).where(
        SimulacionFila.usuario_id == usuario_id, SimulacionFila.estado.in_(["en_cola", "ejecutando"])))


def contar_desde(tx: Session, usuario_id: UUID, desde: datetime) -> int:
    """Simulaciones nuevas del usuario desde `desde`, sin las reutilizadas de la caché (RN5b, RN10)."""
    return tx.scalar(select(func.count()).where(
        SimulacionFila.usuario_id == usuario_id, SimulacionFila.creado_en >= desde,
        ~((SimulacionFila.estado == "completada") & SimulacionFila.iniciada_en.is_(None))))


def contar_en_cola(tx: Session) -> int:
    """Simulaciones esperando en todo el sistema (RN5c)."""
    return tx.scalar(select(func.count()).where(SimulacionFila.estado == "en_cola"))


def listar(tx: Session, usuario_id: UUID, caso_id: Optional[UUID], limite: int,
           despues_de: Optional[UUID]) -> List[Simulacion]:
    """Del más nuevo al más viejo, por cursor (ver decisión 017). Sin resultados: solo el resumen."""
    consulta = select(SimulacionFila).where(SimulacionFila.usuario_id == usuario_id)
    if caso_id:
        consulta = consulta.where(SimulacionFila.caso_id == caso_id)
    if despues_de:
        consulta = consulta.where(SimulacionFila.id < despues_de)
    consulta = consulta.order_by(SimulacionFila.id.desc()).limit(limite)
    return [_a_negocio(tx, f, con_detalle=False) for f in tx.scalars(consulta)]


def buscar(tx: Session, simulacion_id: UUID, usuario_id: UUID) -> Optional[Simulacion]:
    fila = tx.scalars(select(SimulacionFila).where(
        SimulacionFila.id == simulacion_id, SimulacionFila.usuario_id == usuario_id)).first()
    return _a_negocio(tx, fila, con_detalle=True) if fila else None


def buscar_estados_internos(tx: Session, simulacion_id: UUID, usuario_id: UUID) -> Optional[EstadosInternos]:
    """Los estados internos del resultado de una simulación del usuario; None si no es suya o no los tiene."""
    datos = tx.scalar(
        select(EstadosInternosFila.datos)
        .join(SimulacionFila, SimulacionFila.resultado_id == EstadosInternosFila.resultado_id)
        .where(SimulacionFila.id == simulacion_id, SimulacionFila.usuario_id == usuario_id)
    )
    return EstadosInternos(**datos) if datos else None


def tomar_siguiente(tx: Session, ahora: datetime) -> Optional[Simulacion]:
    """
    La simulación más vieja en cola, pasada a ejecutando. SKIP LOCKED: con varios workers, cada uno
    toma una distinta sin esperar a los demás.
    """
    fila = tx.scalars(
        select(SimulacionFila).where(SimulacionFila.estado == "en_cola")
        .order_by(SimulacionFila.id).limit(1).with_for_update(skip_locked=True)
    ).first()
    if fila is None:
        return None
    fila.estado = "ejecutando"
    fila.iniciada_en = ahora
    return _a_negocio(tx, fila, con_detalle=False)


def marcar_completada(tx: Session, simulacion_id: UUID, resultado_id: UUID, ahora: datetime) -> None:
    tx.execute(update(SimulacionFila).where(SimulacionFila.id == simulacion_id)
               .values(estado="completada", resultado_id=resultado_id, finalizada_en=ahora))


def marcar_error(tx: Session, simulacion_id: UUID, mensaje: str, ahora: datetime) -> None:
    tx.execute(update(SimulacionFila).where(SimulacionFila.id == simulacion_id)
               .values(estado="error", mensaje_error=mensaje, finalizada_en=ahora))


def interrumpir_vencidas(tx: Session, iniciadas_antes_de: datetime, mensaje: str, ahora: datetime) -> int:
    """Pasa a error las que siguen ejecutando desde antes de `iniciadas_antes_de`; devuelve cuántas."""
    resultado = tx.execute(
        update(SimulacionFila)
        .where(SimulacionFila.estado == "ejecutando", SimulacionFila.iniciada_en < iniciadas_antes_de)
        .values(estado="error", mensaje_error=mensaje, finalizada_en=ahora)
    )
    return resultado.rowcount
