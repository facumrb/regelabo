"""
Acceso a los perfiles de audición (polos de Shera) guardados en disco.

Cada perfil es una carpeta `data/Poles/<nombre>/` con:
- `StartingPoles.dat`: los polos que usa el modelo (1001 valores: oído medio + 1000 secciones).
- `profile.txt`: la curva del perfil (fila 1 = frecuencia de cada sección en Hz, fila 2 = dB HL).
- `perfil.json`: solo en los personalizados; nombre visible y audiograma pedido.
"""

import json
import os
from functools import lru_cache
from typing import Dict, List, Optional

import numpy as np

POLES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "simulacion", "verhulst", "data", "Poles",
)
ARCHIVO_POLOS = "StartingPoles.dat"
ARCHIVO_CURVA = "profile.txt"
ARCHIVO_DATOS = "perfil.json"


def _ruta(nombre: str, archivo: str) -> str:
    return os.path.join(POLES_DIR, nombre, archivo)


def listar_perfiles() -> List[str]:
    """Nombres de los perfiles disponibles, ordenados alfabéticamente."""
    if not os.path.isdir(POLES_DIR):
        return []
    return [
        nombre for nombre in sorted(os.listdir(POLES_DIR))
        if os.path.isfile(_ruta(nombre, ARCHIVO_POLOS))
    ]


def cargar_polos(nombre: str) -> Optional[np.ndarray]:
    """Devuelve el vector de polos del perfil, o None si no existe."""
    ruta = _ruta(nombre, ARCHIVO_POLOS)
    if not os.path.isfile(ruta):
        return None
    polos = np.loadtxt(ruta)
    return polos[0, :] if polos.ndim > 1 else polos


@lru_cache(maxsize=None)
def cargar_curva(nombre: str) -> Optional[np.ndarray]:
    """Curva (2 x 1000) de un perfil base, o None si no tiene `profile.txt`.
    Se lee una sola vez: los perfiles base no cambian mientras corre el servidor."""
    ruta = _ruta(nombre, ARCHIVO_CURVA)
    return np.loadtxt(ruta) if os.path.isfile(ruta) else None


def cargar_datos_personalizado(nombre: str) -> Optional[Dict]:
    """Nombre visible y audiograma pedido de un perfil personalizado, o None si no los tiene."""
    ruta = _ruta(nombre, ARCHIVO_DATOS)
    if not os.path.isfile(ruta):
        return None
    with open(ruta, encoding="utf-8") as archivo:
        return json.load(archivo)


def guardar_perfil(nombre: str, polos: np.ndarray, datos: Optional[Dict] = None) -> None:
    """Crea o reemplaza el perfil `nombre` con los polos dados (y sus datos, si es personalizado)."""
    os.makedirs(os.path.join(POLES_DIR, nombre), exist_ok=True)
    np.savetxt(_ruta(nombre, ARCHIVO_POLOS), polos, fmt="%.6E")
    if datos is not None:
        with open(_ruta(nombre, ARCHIVO_DATOS), "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False)
