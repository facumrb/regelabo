"""
Tablas de la base de datos (SQLAlchemy).

Son internas a la capa de datos: las funciones de `datos/` las convierten en objetos de
negocio antes de devolverlas. Cualquier cambio acá necesita una migración de Alembic.
"""

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# JSONB en PostgreSQL; JSON genérico en otros motores
JSON_DATOS = JSON().with_variant(JSONB(), "postgresql")


def _valores_fijos(nombre: str, *valores: str) -> Enum:
    """Texto restringido a `valores` con un CHECK (no un ENUM nativo, para migrarlo fácil)."""
    return Enum(*valores, name=nombre, native_enum=False, create_constraint=True, length=20)


class Base(DeclarativeBase):
    type_annotation_map = {
        datetime: DateTime(timezone=True),
        dict[str, Any]: JSON_DATOS,
        list[Any]: JSON_DATOS,
    }


class ConIdYFecha:
    """Columnas comunes: id UUIDv7 (ordenado por tiempo) y fecha de creación."""

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7, sort_order=-1)
    creado_en: Mapped[datetime] = mapped_column(server_default=func.now())


class Usuario(ConIdYFecha, Base):
    __tablename__ = "usuario"

    email: Mapped[str] = mapped_column(String(254), unique=True)  # siempre en minúsculas
    password_hash: Mapped[str] = mapped_column(String(255))
    nombre: Mapped[str] = mapped_column(String(100))
    tipo_perfil: Mapped[str] = mapped_column(
        _valores_fijos("tipo_perfil", "estudiante", "investigador", "fonoaudiologo")
    )
    es_admin: Mapped[bool] = mapped_column(default=False)
    aviso_aceptado_en: Mapped[datetime]  # RN9: aceptación del aviso de uso no profesional
    intentos_fallidos: Mapped[int] = mapped_column(default=0)
    bloqueado_hasta: Mapped[Optional[datetime]]


class Sesion(ConIdYFecha, Base):
    __tablename__ = "sesion"

    usuario_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuario.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)  # SHA-256 del token de la cookie
    expira_en: Mapped[datetime] = mapped_column(index=True)


class Caso(ConIdYFecha, Base):
    __tablename__ = "caso"

    usuario_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuario.id"), index=True)
    alias: Mapped[str] = mapped_column(String(100))
    edad: Mapped[Optional[int]]
    sexo: Mapped[Optional[str]] = mapped_column(_valores_fijos("sexo", "femenino", "masculino", "otro"))
    notas: Mapped[Optional[str]] = mapped_column(Text)
    borrado_en: Mapped[Optional[datetime]]  # borrado lógico: el caso se oculta pero se puede recuperar


class Audiograma(ConIdYFecha, Base):
    __tablename__ = "audiograma"

    caso_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("caso.id"), index=True)
    origen: Mapped[str] = mapped_column(_valores_fijos("origen_audiograma", "manual", "archivo"))
    pta_db: Mapped[float]
    gravedad: Mapped[str] = mapped_column(
        _valores_fijos("gravedad", "normal", "leve", "moderada", "severa")
    )
    patron: Mapped[str] = mapped_column(_valores_fijos("patron", "plano", "pendiente"))
    perfil: Mapped[str] = mapped_column(String(100))  # perfil de polos generado


class PuntoAudiograma(ConIdYFecha, Base):
    __tablename__ = "punto_audiograma"
    __table_args__ = (UniqueConstraint("audiograma_id", "frecuencia_hz"),)  # RN1: sin repetir

    audiograma_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("audiograma.id"), index=True)
    frecuencia_hz: Mapped[float]
    perdida_db: Mapped[float]


class ResultadoSimulacion(ConIdYFecha, Base):
    """Resultado compartido entre todas las simulaciones con la misma huella (RN10)."""

    __tablename__ = "resultado_simulacion"

    huella: Mapped[str] = mapped_column(String(64), unique=True)  # SHA-256 de los parámetros
    efr_uv: Mapped[float]
    armonicos: Mapped[list[Any]]
    espectro: Mapped[dict[str, Any]]
    ondas: Mapped[dict[str, Any]]
    metricas: Mapped[dict[str, Any]]  # latencias y amplitudes de W1, W3, W5
    duracion_s: Mapped[float]


class Simulacion(ConIdYFecha, Base):
    __tablename__ = "simulacion"

    usuario_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuario.id"), index=True)
    caso_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("caso.id"), index=True)
    perfil: Mapped[str] = mapped_column(String(100))
    frecuencia_portadora_hz: Mapped[float]
    nivel_db_spl: Mapped[float]
    frecuencia_modulacion_hz: Mapped[float]
    n_h: Mapped[int]
    n_m: Mapped[int]
    n_l: Mapped[int]
    huella: Mapped[str] = mapped_column(String(64), index=True)
    estado: Mapped[str] = mapped_column(
        _valores_fijos("estado_simulacion", "en_cola", "ejecutando", "completada", "error"),
        index=True,
    )
    resultado_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("resultado_simulacion.id"))
    mensaje_error: Mapped[Optional[str]] = mapped_column(Text)
    iniciada_en: Mapped[Optional[datetime]]
    finalizada_en: Mapped[Optional[datetime]]


class Arquetipo(ConIdYFecha, Base):
    __tablename__ = "arquetipo"

    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    descripcion: Mapped[str] = mapped_column(Text)
    perfil: Mapped[str] = mapped_column(String(100))
    n_h: Mapped[int]
    n_m: Mapped[int]
    n_l: Mapped[int]
    estimulo: Mapped[dict[str, Any]]  # portadora, nivel y modulación del estímulo estándar
    ondas: Mapped[dict[str, Any]]
    metricas: Mapped[dict[str, Any]]
    actualizado_en: Mapped[Optional[datetime]] = mapped_column(onupdate=func.now())


class RegistroABR(ConIdYFecha, Base):
    __tablename__ = "registro_abr"

    caso_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("caso.id"), index=True)
    nombre_archivo: Mapped[str] = mapped_column(String(255))
    fs_hz: Mapped[float]
    senal: Mapped[dict[str, Any]]  # señal normalizada: tiempo (ms) y amplitud (µV)


class Comparacion(ConIdYFecha, Base):
    __tablename__ = "comparacion"

    registro_abr_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("registro_abr.id"), index=True)
    autor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuario.id"))
    # RN8: top 3 con una copia de cada arquetipo, para no depender de cambios posteriores
    coincidencias: Mapped[list[Any]]
    concluyente: Mapped[bool]  # RN7
    arquetipo_elegido_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("arquetipo.id", ondelete="SET NULL")
    )
    hipotesis: Mapped[Optional[str]] = mapped_column(Text)  # hipótesis de estudio, nunca diagnóstico
