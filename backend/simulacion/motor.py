"""
Adaptador del modelo Verhulst et al. (2018).

Es el único punto del backend que conoce cómo se importa y se invoca el código
copiado del modelo (`verhulst/src`). El resto de las capas trabaja con arrays
de NumPy y tipos de Python, sin depender de los módulos internos del modelo.
"""

import os
import sys
import tempfile
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

# Semilla del ruido de la cóclea (`subject` del modelo): fija, así mismos parámetros dan el mismo resultado
SEMILLA = 1
# Entra en la huella de la caché (RN10). Cambiarla si se modifica el código del modelo: invalida los
# resultados guardados, que dejarían de corresponder a lo que calcula el modelo.
VERSION_MODELO = "verhulst2018-1"


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

    # El modelo deja archivos *_0.npz en el directorio de trabajo: cada simulación corre en una carpeta
    # temporal, así dos workers no se pisan y no se ensucia el repo. (chdir es del proceso entero:
    # sirve porque cada worker ejecuta una simulación a la vez.)
    carpeta_original = os.getcwd()
    with tempfile.TemporaryDirectory() as carpeta:
        os.chdir(carpeta)
        try:
            resultados = model2018(
                estimulo,
                FS_ESTIMULO,
                fc='abr',
                irregularities=1,
                storeflag='evihmlbw',
                subject=SEMILLA,
                sheraPo=polos,
                IrrPct=0.05,
                non_linear_type='vel',
                nH=n_h,
                nM=n_m,
                nL=n_l,
                clean=1,
                data_folder='./',
            )
        finally:
            os.chdir(carpeta_original)
    salida = resultados[0] if isinstance(resultados, list) else resultados

    return SalidaModelo(
        fs=float(salida.fs_an),
        w1=salida.w1.flatten(),
        w3=salida.w3.flatten(),
        w5=salida.w5.flatten(),
    )
