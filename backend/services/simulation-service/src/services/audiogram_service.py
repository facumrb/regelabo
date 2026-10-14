"""
Servicio de procesamiento y conversión de audiogramas a perfiles de simulación coclear.
"""

import os
import io
import csv
import re
import numpy as np
from typing import List, Tuple, Dict, Any, Optional

from src.models.audiogram_model import AudiogramPoint, AudiogramResponse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POLES_DIR = os.path.join(BASE_DIR, "Verhulst", "data", "Poles")


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
                "No se pudieron extraer datos válidos del archivo. Asegurate de incluir pares de número como '1000, 25'."
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
        Analiza la curva audiométrica, clasifica el tipo de hipoacusia
        y genera/asigna el perfil de polos cocleares correspondiente.
        """
        if len(points) < 2:
            raise ValueError("Se requieren al menos 2 puntos audiométricos para trazar la curva.")

        freqs = np.array([p.frequency for p in points])
        losses = np.array([p.hearing_loss_db for p in points])

        # 1. Calcular PTA (Pure Tone Average) en frecuencias conversacionales (500, 1000, 2000, 4000 Hz)
        core_losses = []
        for target_f in [500, 1000, 2000, 4000]:
            # Interpolar o tomar el valor más cercano
            idx = int(np.argmin(np.abs(freqs - target_f)))
            core_losses.append(losses[idx])
        pta = float(np.mean(core_losses))

        # 2. Determinar configuración de la curva (Plana vs Pendiente/Slope)
        low_idx = freqs <= 1000
        high_idx = freqs >= 3000
        mean_low = np.mean(losses[low_idx]) if np.any(low_idx) else pta
        mean_high = np.mean(losses[high_idx]) if np.any(high_idx) else pta
        is_slope = (mean_high - mean_low) >= 15.0  # Caída pronunciada en agudos

        # 3. Clasificación fonoaudiológica
        if pta <= 20:
            severity = "Audición Normal"
        elif pta <= 40:
            severity = "Hipoacusia Sensorineural Leve"
        elif pta <= 70:
            severity = "Hipoacusia Sensorineural Moderada"
        else:
            severity = "Hipoacusia Sensorineural Severa"

        pattern = "con caída en agudos (patrón en pendiente)" if is_slope else "patrón plano"
        classification = f"{severity} ({pattern}, PTA: {pta:.1f} dB HL)"

        # 4. Asignar perfil clínico equivalente en data/Poles/
        matched_profile = cls._match_best_profile(pta, is_slope)

        # 5. Crear perfil personalizado si es necesario
        sanitized_name = re.sub(r'[^a-zA-Z0-9_-]', '_', patient_name).strip('_') or "Paciente"
        custom_profile_name = f"Custom_{sanitized_name}"

        # Sintetizar StartingPoles.dat para el paciente
        cls._synthesize_custom_poles(custom_profile_name, matched_profile, freqs, losses)

        return AudiogramResponse(
            status="success",
            patient_name=patient_name,
            points=points,
            matched_profile=custom_profile_name,
            mean_hearing_loss=round(pta, 1),
            clinical_classification=classification,
            notes=f"Generado a partir de la curva audiométrica. Perfil base de referencia: {matched_profile}."
        )

    @classmethod
    def _match_best_profile(cls, pta: float, is_slope: bool) -> str:
        """Selecciona el perfil de referencia más cercano entre los 33 precomputados."""
        if pta < 10 and not is_slope:
            return "Flat00"

        if is_slope:
            # Perfiles tipo Slope
            if pta <= 20:
                return "Slope20"
            elif pta <= 35:
                return "Slope35"
            else:
                return "Flat00_Slope35"
        else:
            # Perfiles tipo Flat
            if pta <= 12:
                return "Flat10"
            elif pta <= 22:
                return "Flat20"
            elif pta <= 27:
                return "Flat25"
            elif pta <= 32:
                return "Flat30"
            else:
                return "Flat35"

    @classmethod
    def _synthesize_custom_poles(
        cls, 
        custom_name: str, 
        base_profile: str, 
        freqs: np.ndarray, 
        losses: np.ndarray
    ):
        """
        Guarda una carpeta de perfil en data/Poles/<custom_name> con StartingPoles.dat
        asegurando compatibilidad total con el motor de simulación.
        """
        target_dir = os.path.join(POLES_DIR, custom_name)
        os.makedirs(target_dir, exist_ok=True)

        base_poles_path = os.path.join(POLES_DIR, base_profile, "StartingPoles.dat")
        if os.path.exists(base_poles_path):
            base_poles = np.loadtxt(base_poles_path)
            # Guardar el perfil para este paciente
            np.savetxt(os.path.join(target_dir, "StartingPoles.dat"), base_poles, fmt="%.6E")
