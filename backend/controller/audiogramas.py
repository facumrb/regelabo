"""
Servicio de procesamiento y conversión de audiogramas a perfiles de simulación coclear.
"""

import re
from typing import List, Literal, Optional
from uuid import UUID

from backend.controller import perfiles
from backend.controller.errores import ErrorDeNegocio
from backend.controller.modelos import AudiogramaGuardado, AudiogramPoint, AudiogramResponse, Usuario
from backend.datos import audiogramas, casos
from backend.datos.conexion import transaccion

_CASO_NO_ENCONTRADO = ErrorDeNegocio("caso_no_encontrado", "El caso no existe.")


class AudiogramService:
    """Procesa audiogramas clínicos y genera o empareja perfiles cocleares."""

    @staticmethod
    def parse_file_content(content_str: str) -> List[AudiogramPoint]:
        """Parsea texto CSV/TXT/TSV con pares de frecuencia y pérdida en dB."""
        points = []
        lines = content_str.strip().splitlines()

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # Separar por coma, punto y coma, tabulador o espacios múltiples
            parts = re.split(r'[,;\t\s]+', line)
            if len(parts) >= 2:
                try:
                    f = float(parts[0])
                    hl = float(parts[1])
                    # Validación básica de rangos audiológicos
                    if 50 <= f <= 20000 and -20 <= hl <= 130:
                        points.append(AudiogramPoint(frequency=f, hearing_loss_db=hl))
                except ValueError:
                    # Ignorar cabeceras tipo "frecuencia,perdida"
                    continue

        if not points:
            raise ValueError(
                "No se pudieron extraer datos válidos del archivo. "
                "Asegurate de incluir pares de número como '1000, 25'."
            )

        # Ordenar por frecuencia ascendente
        points.sort(key=lambda p: p.frequency)
        return points

    @classmethod
    def analyze_and_map(
        cls,
        patient_name: str,
        points: List[AudiogramPoint],
        usuario: Optional[Usuario] = None,
        caso_id: Optional[UUID] = None,
        origen: Literal["manual", "archivo"] = "manual",
    ) -> AudiogramResponse:
        """
        Clasifica la curva audiométrica (RN2) y genera el perfil de polos con su forma
        (ver `controller/perfiles.py`). Con `caso_id`, lo guarda en ese caso del usuario y el perfil
        toma el alias del caso (decisión 032).
        """
        if len(points) < 2:
            raise ValueError("Se requieren al menos 2 puntos audiométricos para trazar la curva.")
        if caso_id is not None:
            with transaccion() as tx:
                caso = casos.buscar(tx, caso_id, usuario.id) if usuario else None
            if caso is None:
                raise _CASO_NO_ENCONTRADO  # ajeno o borrado: no se revela que existe (RN4)
            if len({p.frequency for p in points}) != len(points):
                raise ValueError("Hay frecuencias repetidas: cada frecuencia va una sola vez (RN1).")
            patient_name = caso.alias

        valor_pta = perfiles.pta(points)
        pattern = "patrón en pendiente" if perfiles.patron(points) == "caida_en_agudos" else "patrón plano"
        grado = perfiles.grado(valor_pta)
        nombre_grado = "Audición normal" if grado == "normal" else f"Hipoacusia {grado}"
        classification = f"{nombre_grado} ({pattern}, PTA: {valor_pta:.1f} dB HL)"

        perfil = perfiles.crear_personalizado(patient_name, points)
        notas = "Perfil generado con la forma de tu audiograma."
        if perfil.frecuencias_recortadas:
            notas += (" El modelo solo representa la pérdida de las células ciliadas externas: en "
                      f"{_lista_hz(perfil.frecuencias_recortadas)} se simula menos pérdida que la pedida.")

        audiograma_id = None
        if caso_id is not None:
            with transaccion() as tx:
                audiograma_id = audiogramas.crear(tx, caso_id, origen, round(valor_pta, 1), grado,
                                                  perfiles.patron(points), perfil.nombre, points)

        return AudiogramResponse(
            audiograma_id=audiograma_id,
            status="success",
            patient_name=patient_name,
            points=points,
            matched_profile=perfil.nombre,
            mean_hearing_loss=round(valor_pta, 1),
            clinical_classification=classification,
            notes=notas,
            perfil=perfil,
        )


def _lista_hz(frecuencias: List[float]) -> str:
    return ", ".join(f"{f / 1000:g} kHz" if f >= 1000 else f"{f:g} Hz" for f in frecuencias)


def listar_del_caso(usuario: Usuario, caso_id: UUID) -> List[AudiogramaGuardado]:
    """Los audiogramas de un caso propio, del más nuevo al más viejo (RN4: ajeno o borrado da 404)."""
    with transaccion() as tx:
        if casos.buscar(tx, caso_id, usuario.id) is None:
            raise _CASO_NO_ENCONTRADO
        return audiogramas.listar(tx, caso_id, usuario.id)
