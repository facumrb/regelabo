"""
Simulaciones: validación (RN3), cupos (RN5), caché por huella (RN10) y la cola que consume el worker.

Pedir una simulación nunca ejecuta el modelo: la deja en cola (o, si ya existe un resultado
idéntico, completada al instante). El worker (`worker.py`) llama a `procesar_siguiente`.
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from backend.configuracion import (
    CUPO_POR_HORA, CUPO_SIMULTANEAS, SIMULACION_MINUTOS_MAX, TOPE_COLA,
)
from backend.controller.errores import ErrorDeNegocio
from backend.controller.modelos import (
    EstadosInternos, PaginaDeSimulaciones, ParametrosSimulacion, Simulacion, SimulacionInput, Usuario,
)
from backend.controller.simulacion import SimulationService
from backend.datos import casos, perfiles, simulaciones, usuarios
from backend.datos.conexion import transaccion
from backend.services.motor import SEMILLA, VERSION_MODELO

logger = logging.getLogger(__name__)

# RN3: rango válido de cada parámetro. Los máximos de fibras no están en la regla original:
# son los del prototipo, y evitan que un pedido desmesurado ocupe el servidor.
RANGOS = {
    "spl_level": (0, 100, "El nivel tiene que estar entre 0 y 100 dB SPL."),
    "carrier_freq": (125, 8000, "La frecuencia portadora tiene que estar entre 125 y 8000 Hz."),
    "f_mod": (20, 1000, "La frecuencia de modulación tiene que estar entre 20 y 1000 Hz."),
    "nH": (0, 30, "Las fibras nH tienen que estar entre 0 y 30."),
    "nM": (0, 15, "Las fibras nM tienen que estar entre 0 y 15."),
    "nL": (0, 15, "Las fibras nL tienen que estar entre 0 y 15."),
}

_NO_ENCONTRADA = ErrorDeNegocio("simulacion_no_encontrada", "La simulación no existe.")
# En cola, con error o de una versión del modelo anterior a la decisión 023
_SIN_ESTADOS_INTERNOS = ErrorDeNegocio(
    "estados_internos_no_disponibles",
    "Esta simulación no tiene estados internos: todavía no terminó o se hizo con una versión anterior "
    "del modelo.")


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


def validar_parametros(parametros: ParametrosSimulacion) -> None:
    """RN3. El perfil se valida aparte, porque necesita leer el disco."""
    for campo, (minimo, maximo, mensaje) in RANGOS.items():
        if not minimo <= getattr(parametros, campo) <= maximo:
            raise ErrorDeNegocio("parametros_invalidos", mensaje)
    if parametros.nH + parametros.nM + parametros.nL == 0:
        raise ErrorDeNegocio("parametros_invalidos", "Tiene que haber al menos una fibra (nH + nM + nL > 0).")


def calcular_huella(parametros: ParametrosSimulacion, polos) -> str:
    """
    RN10: identifica un resultado. Incluye un hash del CONTENIDO del perfil y no solo su nombre,
    porque los perfiles Custom_* se pueden regenerar con el mismo nombre.
    """
    datos = {
        "perfil": parametros.poles_profile, "polos": hashlib.sha256(polos.tobytes()).hexdigest(),
        "carrier_freq": parametros.carrier_freq, "spl_level": parametros.spl_level, "f_mod": parametros.f_mod,
        "nH": parametros.nH, "nM": parametros.nM, "nL": parametros.nL,
        "semilla": SEMILLA, "version_modelo": VERSION_MODELO,
    }
    return hashlib.sha256(json.dumps(datos, sort_keys=True).encode()).hexdigest()


def crear(usuario: Usuario, datos: SimulacionInput) -> Simulacion:
    parametros = ParametrosSimulacion(**datos.model_dump(exclude={"caso_id"}))
    validar_parametros(parametros)
    polos = perfiles.cargar_polos(parametros.poles_profile)
    if polos is None:
        raise ErrorDeNegocio("perfil_inexistente", f"El perfil '{parametros.poles_profile}' no existe.")
    huella = calcular_huella(parametros, polos)
    ahora = _ahora()

    with transaccion() as tx:
        if datos.caso_id and casos.buscar(tx, datos.caso_id, usuario.id) is None:
            raise ErrorDeNegocio("caso_no_encontrado", "El caso no existe.")  # RN4
        usuarios.bloquear(tx, usuario.id)  # los pedidos de un mismo usuario se verifican de a uno

        resultado_id = simulaciones.buscar_resultado_id(tx, huella)
        if resultado_id is None:  # solo lo que va a la cola consume cupo (RN10)
            # shortcut: el tope global no se bloquea, con pedidos simultáneos de varios usuarios puede
            # pasarse por poco; alcanza para proteger al servidor
            if simulaciones.contar_en_cola(tx) >= TOPE_COLA:
                raise ErrorDeNegocio("sistema_saturado", "Sistema saturado, reintentá en unos minutos.")
            if simulaciones.contar_activas(tx, usuario.id) >= CUPO_SIMULTANEAS[usuario.tipo_perfil]:
                raise ErrorDeNegocio("cupo_agotado",
                                     "Ya tenés el máximo de simulaciones en curso. Esperá a que termine una.")
            ultima_hora = simulaciones.contar_desde(tx, usuario.id, ahora - timedelta(hours=1))
            if ultima_hora >= CUPO_POR_HORA[usuario.tipo_perfil]:
                raise ErrorDeNegocio("limite_por_hora",
                                     "Llegaste al máximo de simulaciones por hora. Reintentá más tarde.")

        simulacion_id = simulaciones.crear(tx, usuario.id, datos.caso_id, parametros, huella,
                                           resultado_id, ahora)
    return ver(usuario, simulacion_id)


def listar(usuario: Usuario, caso_id: Optional[UUID], limite: int,
           despues_de: Optional[UUID]) -> PaginaDeSimulaciones:
    with transaccion() as tx:
        # uno de más: dice si hay página siguiente
        pagina = simulaciones.listar(tx, usuario.id, caso_id, limite + 1, despues_de)
    hay_mas = len(pagina) > limite
    pagina = pagina[:limite]
    return PaginaDeSimulaciones(simulaciones=pagina, siguiente=pagina[-1].id if hay_mas else None)


def ver(usuario: Usuario, simulacion_id: UUID) -> Simulacion:
    with transaccion() as tx:
        simulacion = simulaciones.buscar(tx, simulacion_id, usuario.id)
    if simulacion is None:
        raise _NO_ENCONTRADA
    return simulacion


def ver_estados_internos(usuario: Usuario, simulacion_id: UUID) -> EstadosInternos:
    with transaccion() as tx:
        estados = simulaciones.buscar_estados_internos(tx, simulacion_id, usuario.id)
        existe = estados is not None or simulaciones.buscar(tx, simulacion_id, usuario.id) is not None
    if estados is None:
        raise _SIN_ESTADOS_INTERNOS if existe else _NO_ENCONTRADA
    return estados


# ---- Lo que usa el worker ----

def procesar_siguiente() -> bool:
    """Toma la simulación más vieja en cola y la ejecuta. Devuelve False si no había ninguna."""
    with transaccion() as tx:
        simulacion = simulaciones.tomar_siguiente(tx, _ahora())
    if simulacion is None:
        return False

    respuesta = None
    mensaje = ""
    try:
        respuesta = SimulationService.execute_simulation(simulacion.parametros)
    except ValueError as error:  # los errores previstos del servicio tienen mensajes propios
        mensaje = str(error)
    except Exception:
        logger.exception("Falló la simulación %s", simulacion.id)
        mensaje = "No se pudo completar la simulación. Probá de nuevo."

    with transaccion() as tx:
        if respuesta is not None:
            resultado_id = simulaciones.guardar_resultado(tx, simulacion.huella, respuesta)
            simulaciones.marcar_completada(tx, simulacion.id, resultado_id, _ahora())
        else:
            simulaciones.marcar_error(tx, simulacion.id, mensaje, _ahora())
    return True


def recuperar_interrumpidas() -> int:
    """Pasa a error las simulaciones que llevan demasiado ejecutando (el worker se cayó): libera su cupo."""
    ahora = _ahora()
    with transaccion() as tx:
        return simulaciones.interrumpir_vencidas(
            tx, ahora - timedelta(minutes=SIMULACION_MINUTOS_MAX),
            "La simulación se interrumpió. Podés volver a pedirla.", ahora)
