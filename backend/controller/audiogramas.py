"""
Servicio de procesamiento y conversión de audiogramas a perfiles de simulación coclear.
"""

import re
from typing import List

import numpy as np

from backend.controller import perfiles
from backend.controller.modelos import AudiogramPoint, AudiogramResponse


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
        points: List[AudiogramPoint]
    ) -> AudiogramResponse:
        """
        Clasifica la curva audiométrica (RN2) y genera el perfil de polos con su forma
        (ver `controller/perfiles.py`).
        """
        if len(points) < 2:
            raise ValueError("Se requieren al menos 2 puntos audiométricos para trazar la curva.")

        freqs = np.array([p.frequency for p in points])
        losses = np.array([p.hearing_loss_db for p in points])
        valor_pta = perfiles.pta(points)

        # RN2: patrón en pendiente si los agudos (>= 3 kHz) pierden >= 15 dB más que los graves (<= 1 kHz)
        low_idx = freqs <= 1000
        high_idx = freqs >= 3000
        mean_low = np.mean(losses[low_idx]) if np.any(low_idx) else valor_pta
        mean_high = np.mean(losses[high_idx]) if np.any(high_idx) else valor_pta
        pattern = "patrón en pendiente" if mean_high - mean_low >= 15.0 else "patrón plano"
        grado = perfiles.grado(valor_pta)
        nombre_grado = "Audición normal" if grado == "normal" else f"Hipoacusia {grado}"
        classification = f"{nombre_grado} ({pattern}, PTA: {valor_pta:.1f} dB HL)"

        perfil = perfiles.crear_personalizado(patient_name, points)
        notas = "Perfil generado con la forma de tu audiograma."
        if perfil.frecuencias_recortadas:
            notas += (" El modelo solo representa la pérdida de las células ciliadas externas: en "
                      f"{_lista_hz(perfil.frecuencias_recortadas)} se simula menos pérdida que la pedida.")

        return AudiogramResponse(
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
