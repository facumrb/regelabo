"""
Acceso a los usuarios. Todas las funciones reciben la sesión de `transaccion()`
y devuelven objetos de negocio, nunca filas de la base.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from sqlalchemy import case, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.controller.modelos import TipoPerfil, Usuario, UsuarioAdmin
from backend.datos.tablas import Caso as CasoFila
from backend.datos.tablas import Simulacion as SimulacionFila
from backend.datos.tablas import Usuario as UsuarioFila


def buscar_por_email(tx: Session, email: str) -> Optional[Usuario]:
    fila = tx.scalars(select(UsuarioFila).where(UsuarioFila.email == email)).first()
    return Usuario.model_validate(fila) if fila else None


def crear(tx: Session, email: str, password_hash: str, nombre: str, tipo_perfil: str,
          es_admin: bool, aviso_aceptado_en: datetime,
          email_verificado_en: Optional[datetime] = None) -> Optional[Usuario]:
    """Crea el usuario; devuelve None si el email ya existe."""
    fila = UsuarioFila(email=email, password_hash=password_hash, nombre=nombre,
                       tipo_perfil=tipo_perfil, es_admin=es_admin, aviso_aceptado_en=aviso_aceptado_en,
                       email_verificado_en=email_verificado_en)
    try:
        with tx.begin_nested():  # savepoint: el choque con el email único no arruina la transacción
            tx.add(fila)
    except IntegrityError:
        return None
    return Usuario.model_validate(fila)


def bloquear(tx: Session, usuario_id: UUID) -> None:
    """Bloquea la fila del usuario hasta el fin de la transacción: dos pedidos suyos se hacen en fila."""
    tx.execute(select(UsuarioFila.id).where(UsuarioFila.id == usuario_id).with_for_update())


def marcar_admin(tx: Session, usuario_id: UUID, ahora: datetime) -> None:
    """Los admin se crean por comando: quedan con el email verificado (RN15)."""
    verificado = func.coalesce(UsuarioFila.email_verificado_en, ahora)
    tx.execute(update(UsuarioFila).where(UsuarioFila.id == usuario_id)
               .values(es_admin=True, email_verificado_en=verificado))


def marcar_verificado(tx: Session, usuario_id: UUID, ahora: datetime) -> None:
    """RN15. Si ya estaba verificado conserva la fecha original."""
    tx.execute(update(UsuarioFila)
               .where(UsuarioFila.id == usuario_id, UsuarioFila.email_verificado_en.is_(None))
               .values(email_verificado_en=ahora))


def registrar_fallo(tx: Session, usuario_id: UUID, ahora: datetime, intentos_max: int,
                    bloqueo: timedelta) -> None:
    """
    Suma un intento fallido. Al llegar al máximo bloquea la cuenta y reinicia el contador.
    Es un solo UPDATE, así que dos intentos simultáneos no se pisan.
    """
    llega_al_maximo = UsuarioFila.intentos_fallidos + 1 >= intentos_max
    tx.execute(
        update(UsuarioFila).where(UsuarioFila.id == usuario_id).values(
            intentos_fallidos=case((llega_al_maximo, 0), else_=UsuarioFila.intentos_fallidos + 1),
            bloqueado_hasta=case((llega_al_maximo, ahora + bloqueo), else_=UsuarioFila.bloqueado_hasta),
        )
    )


def cambiar_contrasena(tx: Session, usuario_id: UUID, password_hash: str, temporal: bool = False) -> None:
    """Guarda el hash nuevo, desbloquea la cuenta y da por atendido un pedido de restablecimiento.
    `temporal`: la conoce un admin, así que el usuario tendrá que elegir otra al entrar."""
    tx.execute(update(UsuarioFila).where(UsuarioFila.id == usuario_id)
               .values(password_hash=password_hash, intentos_fallidos=0, bloqueado_hasta=None,
                       restablecimiento_pedido_en=None, debe_cambiar_contrasena=temporal))


def pedir_restablecimiento(tx: Session, usuario_id: UUID, ahora: datetime) -> None:
    tx.execute(update(UsuarioFila).where(UsuarioFila.id == usuario_id)
               .values(restablecimiento_pedido_en=ahora))


def contar_pedidos_de_restablecimiento(tx: Session) -> int:
    return tx.scalar(select(func.count()).where(UsuarioFila.restablecimiento_pedido_en.is_not(None)))


def reiniciar_intentos(tx: Session, usuario_id: UUID) -> None:
    tx.execute(update(UsuarioFila).where(UsuarioFila.id == usuario_id)
               .values(intentos_fallidos=0, bloqueado_hasta=None))


def buscar(tx: Session, usuario_id: UUID) -> Optional[Usuario]:
    fila = tx.get(UsuarioFila, usuario_id)
    return Usuario.model_validate(fila) if fila else None


def _con_totales():
    """Usuarios con la cantidad de casos (sin los borrados) y de simulaciones: nunca su contenido (RN4)."""
    casos = (select(func.count()).where(CasoFila.usuario_id == UsuarioFila.id, CasoFila.borrado_en.is_(None))
             .correlate(UsuarioFila).scalar_subquery())
    simulaciones = (select(func.count()).where(SimulacionFila.usuario_id == UsuarioFila.id)
                    .correlate(UsuarioFila).scalar_subquery())
    return select(UsuarioFila, casos, simulaciones)


def _usuario_admin(fila: UsuarioFila, casos: int, simulaciones: int) -> UsuarioAdmin:
    return UsuarioAdmin(id=fila.id, email=fila.email, nombre=fila.nombre, tipo_perfil=fila.tipo_perfil,
                        es_admin=fila.es_admin, creado_en=fila.creado_en,
                        bloqueado_hasta=fila.bloqueado_hasta,
                        email_verificado=fila.email_verificado_en is not None,
                        restablecimiento_pedido_en=fila.restablecimiento_pedido_en,
                        casos=casos, simulaciones=simulaciones)


def listar_para_admin(tx: Session, limite: int, despues_de: Optional[UUID], busqueda: Optional[str],
                      tipo: Optional[TipoPerfil], con_pedido: bool = False) -> List[UsuarioAdmin]:
    """Del más nuevo al más viejo, paginado por cursor. `busqueda`: parte del email o del nombre."""
    consulta = _con_totales().order_by(UsuarioFila.id.desc()).limit(limite)
    if con_pedido:
        consulta = consulta.where(UsuarioFila.restablecimiento_pedido_en.is_not(None))
    if busqueda:
        consulta = consulta.where(UsuarioFila.email.icontains(busqueda, autoescape=True)
                                  | UsuarioFila.nombre.icontains(busqueda, autoescape=True))
    if tipo:
        consulta = consulta.where(UsuarioFila.tipo_perfil == tipo)
    if despues_de:
        consulta = consulta.where(UsuarioFila.id < despues_de)
    return [_usuario_admin(*fila) for fila in tx.execute(consulta)]


def ver_para_admin(tx: Session, usuario_id: UUID) -> UsuarioAdmin:
    return _usuario_admin(*tx.execute(_con_totales().where(UsuarioFila.id == usuario_id)).one())
