"""
Acceso a los perfiles de audición (polos de Shera) guardados en disco.

Cada perfil es una carpeta `data/Poles/<nombre>/` con un archivo `StartingPoles.dat`.
"""

import os
from typing import List, Optional

import numpy as np

POLES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "simulacion", "verhulst", "data", "Poles",
)
ARCHIVO_POLOS = "StartingPoles.dat"


def _ruta_polos(nombre: str) -> str:
    return os.path.join(POLES_DIR, nombre, ARCHIVO_POLOS)


def listar_perfiles() -> List[str]:
    """Nombres de los perfiles disponibles, ordenados alfabéticamente."""
    if not os.path.isdir(POLES_DIR):
        return []
    return [
        nombre for nombre in sorted(os.listdir(POLES_DIR))
        if os.path.isfile(_ruta_polos(nombre))
    ]


def cargar_polos(nombre: str) -> Optional[np.ndarray]:
    """Devuelve el vector de polos del perfil, o None si no existe."""
    ruta = _ruta_polos(nombre)
    if not os.path.isfile(ruta):
        return None
    polos = np.loadtxt(ruta)
    return polos[0, :] if polos.ndim > 1 else polos


def guardar_perfil(nombre: str, polos: np.ndarray) -> None:
    """Crea o reemplaza el perfil `nombre` con los polos dados."""
    os.makedirs(os.path.join(POLES_DIR, nombre), exist_ok=True)
    np.savetxt(_ruta_polos(nombre), polos, fmt="%.6E")
