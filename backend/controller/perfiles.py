"""
Perfiles auditivos: catálogo con etiquetas para el profesional, techo del modelo y perfiles personalizados.

El modelo solo representa la pérdida de las células ciliadas externas (OHC): su polo se satura al daño
máximo, y desde ahí más dB pedidos ya no cambian nada. Ese techo depende de la frecuencia (~20 dB HL en
250 Hz, ~35 dB HL en 8 kHz). Por eso cada perfil muestra la curva pedida y la que realmente se simula.

Los polos de un audiograma nuevo salen de la tabla "dB HL -> polo" de los 8 perfiles planos (Flat00..Flat35),
sección por sección: es la búsqueda de `OHC_ind`, con una tabla más gruesa (decisión 022). Validada
reconstruyendo los perfiles descendentes: error medio 0,18 dB, máximo 4,7 dB.
"""

import hashlib
import json
import re
from functools import lru_cache
from typing import List, Optional, Tuple

import numpy as np

from backend.controller.errores import ErrorDeNegocio
from backend.controller.modelos import AudiogramPoint, PerfilAuditivo
from backend.datos import perfiles

NIVELES_PLANOS = [0, 5, 10, 15, 20, 25, 30, 35]
FRECUENCIAS_AUDIOMETRIA = [250, 500, 1000, 2000, 4000, 8000]
FRECUENCIAS_PTA = [500, 1000, 2000, 4000]
RECORTE_AVISO_DB = 5  # Q19: más de un paso de audiometría
PREFIJO_PERSONALIZADO = "Custom_"

# Repiten los polos de otro perfil de la lista (dif. < 6 %): se ocultan para no confundir.
# "Normal" tiene polos de audición normal (como Flat00), pero su profile.txt dice otra cosa.
DUPLICADOS = {"Normal", "Slope00", "Flat00_Slope00", "Slope05_5"} | {
    f"Flat00_Slope{n:02d}" for n in range(5, 40, 5)
}

# Distinto de "perfil_inexistente" (400, RN3 al pedir una simulación): acá es un recurso que no está
_NO_EXISTE = ErrorDeNegocio("perfil_no_encontrado", "El perfil no existe.")


# ---- Tabla del modelo ----

@lru_cache(maxsize=1)
def _tabla() -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(frecuencia de cada sección, polos de los planos [8 x 1000], techo en dB HL por sección)."""
    frecuencias = perfiles.cargar_curva("Flat00")[0]
    polos = np.array([perfiles.cargar_polos(f"Flat{n:02d}")[1:] for n in NIVELES_PLANOS])
    # shortcut: el techo es el primer nivel saturado (paso de 5 dB); el real puede estar hasta 5 dB abajo
    saturado = np.isclose(polos, polos.max(axis=0))
    techo = np.array(NIVELES_PLANOS, dtype=float)[saturado.argmax(axis=0)]
    return frecuencias, polos, techo


def _seccion(frecuencia: float) -> int:
    return int(np.argmin(np.abs(_tabla()[0] - frecuencia)))


def _por_seccion(puntos: List[AudiogramPoint]) -> np.ndarray:
    """Interpola el audiograma sobre las 1000 secciones, como `OHC_ind` (lineal en el índice de sección)."""
    pares = sorted((_seccion(p.frequency), p.hearing_loss_db) for p in puntos)
    indices, valores = zip(*pares)
    return np.interp(np.arange(len(_tabla()[0])), indices, valores)


def generar_polos(puntos: List[AudiogramPoint]) -> np.ndarray:
    """Polos (1001) que siguen la forma del audiograma, saturados donde el modelo no alcanza."""
    _, polos_planos, _ = _tabla()
    perdida = _por_seccion(puntos)
    secciones = [np.interp(perdida[k], NIVELES_PLANOS, polos_planos[:, k]) for k in range(len(perdida))]
    return np.concatenate([[secciones[0]], secciones])  # el polo 0 (oído medio) repite el 1


def curva_simulada(puntos: List[AudiogramPoint]) -> List[AudiogramPoint]:
    """Lo que el modelo puede representar de cada punto: entre 0 dB HL y el techo de esa frecuencia."""
    techo = _tabla()[2]
    return [AudiogramPoint(frequency=p.frequency,
                           hearing_loss_db=float(np.clip(p.hearing_loss_db, 0, techo[_seccion(p.frequency)])))
            for p in puntos]


# ---- Clasificación (RN2) ----

def pta(puntos: List[AudiogramPoint]) -> float:
    """Promedio en 500, 1000, 2000 y 4000 Hz (el punto más cercano a cada una)."""
    frecuencias = np.array([p.frequency for p in puntos])
    return float(np.mean([puntos[int(np.argmin(np.abs(frecuencias - f)))].hearing_loss_db
                          for f in FRECUENCIAS_PTA]))


def grado(valor_pta: float) -> str:
    if valor_pta <= 20:
        return "normal"
    if valor_pta <= 40:
        return "leve"
    if valor_pta <= 70:
        return "moderada"
    return "severa"


# ---- Catálogo ----

def _etiqueta_base(nombre: str) -> Tuple[str, str]:
    """(forma, descripción) a partir del nombre de la carpeta (convención del README de Verhulst)."""
    if m := re.fullmatch(r"Flat(\d+)", nombre):
        db = int(m[1])
        return "plana", "Sin pérdida (0 dB HL)" if db == 0 else f"Plana · {db} dB HL en todas las frecuencias"
    if m := re.fullmatch(r"Slope(\d+)(?:_(\d+))?", nombre):
        texto = f"Descendente desde 1 kHz · {int(m[1])} dB HL a 8 kHz"
        return "descendente", texto + (f", graves en {int(m[2])} dB HL" if m[2] else "")
    if m := re.fullmatch(r"Flat(\d+)_Slope(\d+)", nombre):
        return "combinada", f"Plana {int(m[1])} dB HL + descendente hasta {int(m[2])} dB HL a 8 kHz"
    return "plana", nombre


def _armar(nombre: str, forma: str, descripcion: str, pedida: List[AudiogramPoint]) -> PerfilAuditivo:
    simulada = curva_simulada(pedida)
    valor_pta = round(pta(pedida), 1)
    return PerfilAuditivo(
        nombre=nombre, forma=forma, grado=grado(valor_pta), pta=valor_pta,
        etiqueta=f"{descripcion} · {grado(valor_pta)} (PTA {valor_pta:g})",
        curva_pedida=pedida, curva_simulada=simulada,
        frecuencias_recortadas=[p.frequency for p, s in zip(pedida, simulada)
                                if p.hearing_loss_db - s.hearing_loss_db > RECORTE_AVISO_DB],
    )


def _perfil_base(nombre: str) -> Optional[PerfilAuditivo]:
    curva = perfiles.cargar_curva(nombre)
    if curva is None:
        return None
    pedida = [AudiogramPoint(frequency=f, hearing_loss_db=round(float(curva[1][_seccion(f)]), 1))
              for f in FRECUENCIAS_AUDIOMETRIA]
    return _armar(nombre, *_etiqueta_base(nombre), pedida)


def _perfil_personalizado(nombre: str) -> Optional[PerfilAuditivo]:
    datos = perfiles.cargar_datos_personalizado(nombre)
    if datos is None:  # los generados antes de la decisión 022 no guardaban el audiograma
        return None
    pedida = [AudiogramPoint(**p) for p in datos["pedida"]]
    return _armar(nombre, "personalizada", f"{datos['etiqueta']} (personalizado)", pedida)


def listar() -> List[PerfilAuditivo]:
    """Los perfiles base, sin duplicados.
    Los personalizados no se listan: los vería cualquier usuario (RN4)."""
    nombres = [n for n in perfiles.listar_perfiles()
               if not n.startswith(PREFIJO_PERSONALIZADO) and n not in DUPLICADOS]
    orden = {"plana": 0, "descendente": 1, "combinada": 2}
    lista = [p for p in map(_perfil_base, nombres) if p is not None]
    return sorted(lista, key=lambda p: (orden[p.forma], p.pta, p.nombre))


def ver(nombre: str) -> PerfilAuditivo:
    if perfiles.cargar_polos(nombre) is None:
        raise _NO_EXISTE
    personalizado = nombre.startswith(PREFIJO_PERSONALIZADO)
    perfil = _perfil_personalizado(nombre) if personalizado else _perfil_base(nombre)
    if perfil is None:
        raise _NO_EXISTE
    return perfil


def crear_personalizado(etiqueta: str, puntos: List[AudiogramPoint]) -> PerfilAuditivo:
    """Genera (o reusa) el perfil de un audiograma. La carpeta se nombra por el contenido: nunca se pisa
    otro perfil, y el nombre que escribió el usuario no forma parte de la ruta."""
    pedida = [p.model_dump() for p in sorted(puntos, key=lambda p: p.frequency)]
    contenido = json.dumps({"etiqueta": etiqueta, "pedida": pedida}, sort_keys=True)
    nombre = PREFIJO_PERSONALIZADO + hashlib.sha256(contenido.encode()).hexdigest()[:16]
    perfiles.guardar_perfil(nombre, generar_polos(puntos), {"etiqueta": etiqueta, "pedida": pedida})
    return ver(nombre)
