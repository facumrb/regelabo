"""
Adaptador del modelo Verhulst et al. (2018).

Es el único punto del backend que conoce cómo se importa y se invoca el código
copiado del modelo (`verhulst/src`). El resto de las capas trabaja con arrays
de NumPy y tipos de Python, sin depender de los módulos internos del modelo.
"""

import os
import sys
from dataclasses import dataclass

import numpy as np

# El código de Verhulst se importa como módulos top-level (`model2018`, `core`,
# `utils`), por eso su carpeta `src` tiene que estar en el path.
VERHULST_SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verhulst", "src")
if VERHULST_SRC not in sys.path:
    sys.path.insert(0, VERHULST_SRC)

from model2018 import model2018  # noqa: E402
from utils.get_RAM_stims import get_RAM_stims  # noqa: E402

# Frecuencia de muestreo del estímulo: 100 kHz para la precisión temporal de la membrana basilar
FS_ESTIMULO = 1e5
DURACION_ESTIMULO_S = 0.4


@dataclass
class SalidaModelo:
    """Ondas ABR crudas (en voltios) que devuelve el modelo."""

    fs: float
    w1: np.ndarray
    w3: np.ndarray
    w5: np.ndarray


def solver_c_disponible() -> bool:
    """Indica si se cargó la biblioteca C (`tridiag.so`) o el modelo usa el fallback en Python."""
    try:
        from core.cochlear_model2018 import HAS_CLIB
    except Exception:
        return False
    return bool(HAS_CLIB)


def ejecutar_modelo(
    polos: np.ndarray,
    frecuencia_portadora: float,
    nivel_db_spl: float,
    frecuencia_modulacion: float,
    n_h: int,
    n_m: int,
    n_l: int,
) -> SalidaModelo:
    """Genera el estímulo RAM y ejecuta el modelo completo (cóclea → IHC → AN → CN/IC)."""
    estimulo = get_RAM_stims(
        fs=FS_ESTIMULO,
        fRAM=np.array([frecuencia_portadora]),
        level=nivel_db_spl,
        fMod=frecuencia_modulacion,
        dur=DURACION_ESTIMULO_S,
    )

    resultados = model2018(
        estimulo,
        FS_ESTIMULO,
        fc='abr',
        irregularities=1,
        storeflag='evihmlbw',
        subject=1,
        sheraPo=polos,
        IrrPct=0.05,
        non_linear_type='vel',
        nH=n_h,
        nM=n_m,
        nL=n_l,
        clean=1,
        data_folder='./',
    )
    salida = resultados[0] if isinstance(resultados, list) else resultados

    return SalidaModelo(
        fs=float(salida.fs_an),
        w1=salida.w1.flatten(),
        w3=salida.w3.flatten(),
        w5=salida.w5.flatten(),
    )
