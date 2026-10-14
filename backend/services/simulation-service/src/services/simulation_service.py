"""
Servicio de simulación biológica de la vía auditiva periférica humana (Verhulst 2018).
"""

import os
import sys
import time
import numpy as np
from typing import List, Dict, Any, Tuple

# Rutas hacia el código del modelo Verhulst
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERHULST_DIR = os.path.join(BASE_DIR, "Verhulst")
VERHULST_SRC = os.path.join(VERHULST_DIR, "src")
POLES_DIR = os.path.join(VERHULST_DIR, "data", "Poles")

# Agregar paths si no están en sys.path
if VERHULST_SRC not in sys.path:
    sys.path.insert(0, VERHULST_SRC)

from model2018 import model2018  # noqa: E402
from utils.get_RAM_stims import get_RAM_stims  # noqa: E402
from src.models.simulation_model import (  # noqa: E402
    SimulationRequest,
    SimulationResponse,
    SpectrumData,
    ABRWavesData,
    HarmonicPeak,
)


class SimulationService:
    """Orquestador de simulaciones biológicas."""

    @staticmethod
    def list_available_profiles() -> List[str]:
        """Retorna los nombres de los perfiles de polos disponibles en data/Poles/."""
        if not os.path.exists(POLES_DIR):
            return ["Flat00", "Normal"]
        profiles = []
        for d in sorted(os.listdir(POLES_DIR)):
            full_path = os.path.join(POLES_DIR, d)
            poles_file = os.path.join(full_path, "StartingPoles.dat")
            if os.path.isdir(full_path) and os.path.exists(poles_file):
                profiles.append(d)
        return profiles

    @classmethod
    def execute_simulation(cls, req: SimulationRequest) -> SimulationResponse:
        """
        Ejecuta el pipeline completo de simulación:
        1. Carga de polos auditivos
        2. Generación del estímulo acústico RAM
        3. Simulación biológica en cóclea, sinapsis y tronco encefálico
        4. Extracción de ABR, EFR y espectro FFT
        """
        start_time = time.time()

        # 1. Validar y cargar perfil de polos
        profile_path = os.path.join(POLES_DIR, req.poles_profile, "StartingPoles.dat")
        if not os.path.exists(profile_path):
            available = cls.list_available_profiles()
            raise ValueError(
                f"Perfil '{req.poles_profile}' no encontrado. Disponibles: {available[:5]}..."
            )

        sheraP = np.loadtxt(profile_path)
        if sheraP.ndim > 1:
            sheraP = sheraP[0, :]

        # 2. Configurar y generar estímulo RAM
        fs = 1e5  # 100 kHz de muestreo para precisión temporal de la membrana basilar
        fRAM = np.array([req.carrier_freq])

        stimulus = get_RAM_stims(
            fs=fs,
            fRAM=fRAM,
            level=req.spl_level,
            fMod=req.f_mod,
            dur=0.4
        )

        # 3. Ejecutar simulación biológica (Verhulst et al. 2018)
        results = model2018(
            stimulus,
            fs,
            fc='abr',
            irregularities=1,
            storeflag='evihmlbw',
            subject=1,
            sheraPo=sheraP,
            IrrPct=0.05,
            non_linear_type='vel',
            nH=req.nH,
            nM=req.nM,
            nL=req.nL,
            clean=1,
            data_folder='./'
        )

        output = results[0] if isinstance(results, list) else results

        # 4. Procesar ondas ABR y EFR
        fs_an = float(output.fs_an)
        w1 = output.w1.flatten()
        w3 = output.w3.flatten()
        w5 = output.w5.flatten()
        efr_wave = w1 + w3 + w5

        # 5. Cálculo FFT y Armónicos del EFR
        L = len(efr_wave)
        Y = np.fft.fft(efr_wave)
        P2 = np.abs(Y / L)
        P1 = P2[:L // 2 + 1]
        P1[1:-1] = 2 * P1[1:-1]
        f_vec = fs_an * np.arange(L // 2 + 1) / L

        # Identificar armónicos
        harmonic_peaks: List[HarmonicPeak] = []
        harmonic_sum_uv = 0.0
        for order in range(1, 5):
            target_f = order * req.f_mod
            idx = int(np.argmin(np.abs(f_vec - target_f)))
            amp_uv = float(P1[idx] * 1e6)
            harmonic_sum_uv += amp_uv
            harmonic_peaks.append(
                HarmonicPeak(
                    harmonic_order=order,
                    frequency_hz=round(float(f_vec[idx]), 1),
                    amplitude_uv=round(amp_uv, 4)
                )
            )

        # Filtrar espectro a la región relevante (0 - 1000 Hz) para transferencia liviana
        fft_mask = (f_vec >= 0) & (f_vec <= 1000)
        spectrum_data = SpectrumData(
            frequencies=[round(float(x), 1) for x in f_vec[fft_mask]],
            amplitudes=[round(float(x * 1e6), 4) for x in P1[fft_mask]]
        )

        # 6. Decimación para visualización web fluida (< 800 puntos)
        time_vec_ms = (np.arange(L) / fs_an) * 1000.0
        step = max(1, L // 750)

        abr_data = ABRWavesData(
            time_ms=[round(float(t), 2) for t in time_vec_ms[::step]],
            w1=[round(float(v * 1e6), 4) for v in w1[::step]],
            w3=[round(float(v * 1e6), 4) for v in w3[::step]],
            w5=[round(float(v * 1e6), 4) for v in w5[::step]],
            efr_wave=[round(float(v * 1e6), 4) for v in efr_wave[::step]]
        )

        exec_time = time.time() - start_time

        return SimulationResponse(
            status="success",
            execution_time_seconds=round(exec_time, 2),
            efr_value_uv=round(harmonic_sum_uv, 4),
            harmonics=harmonic_peaks,
            fft_spectrum=spectrum_data,
            abr_waves=abr_data,
            parameters_used={
                "carrier_freq": req.carrier_freq,
                "poles_profile": req.poles_profile,
                "spl_level": req.spl_level,
                "f_mod": req.f_mod,
                "nH": req.nH,
                "nM": req.nM,
                "nL": req.nL
            }
        )
