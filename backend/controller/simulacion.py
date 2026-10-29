"""
Lógica de negocio de la simulación biológica de la vía auditiva periférica (Verhulst 2018).
"""

import time
from typing import Any, Dict, List

import numpy as np

from backend.controller.modelos import (
    ABRWavesData,
    EstadosInternos,
    HarmonicPeak,
    ParametrosSimulacion,
    SimulationResponse,
    SpectrumData,
)
from backend.datos import perfiles
from backend.services import motor


class SimulationService:
    """Orquestador de simulaciones biológicas."""

    @staticmethod
    def get_engine_status() -> Dict[str, Any]:
        """Estado del motor de simulación y disponibilidad del solver en C."""
        return {
            "status": "online",
            "service": "simulation-service",
            "c_solver_available": motor.solver_c_disponible(),
        }

    @staticmethod
    def list_available_profiles() -> List[str]:
        """Retorna los nombres de los perfiles de polos disponibles."""
        return perfiles.listar_perfiles()

    @classmethod
    def execute_simulation(cls, req: ParametrosSimulacion) -> SimulationResponse:
        """
        Ejecuta el pipeline completo de simulación:
        1. Carga de polos auditivos
        2. Simulación biológica en cóclea, sinapsis y tronco encefálico
        3. Extracción de ABR, EFR y espectro FFT
        """
        start_time = time.time()

        # 1. Validar y cargar perfil de polos
        sheraP = perfiles.cargar_polos(req.poles_profile)
        if sheraP is None:
            available = cls.list_available_profiles()
            raise ValueError(
                f"Perfil '{req.poles_profile}' no encontrado. Disponibles: {available[:5]}..."
            )

        # 2. Ejecutar simulación biológica (Verhulst et al. 2018)
        output = motor.ejecutar_modelo(
            polos=sheraP,
            frecuencia_portadora=req.carrier_freq,
            nivel_db_spl=req.spl_level,
            frecuencia_modulacion=req.f_mod,
            n_h=req.nH,
            n_m=req.nM,
            n_l=req.nL,
        )

        # 3. Procesar ondas ABR y EFR
        fs_an = output.fs
        w1, w3, w5 = output.w1, output.w3, output.w5
        efr_wave = w1 + w3 + w5

        # 4. Cálculo FFT y Armónicos del EFR
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

        # 5. Decimación para visualización web fluida (< 800 puntos)
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
            },
            estados_internos=EstadosInternos(**_a_listas(output.estados_internos)),
        )


def _a_listas(valor, cifras: int = 5):
    """Convierte los arreglos de NumPy a listas con `cifras` cifras significativas (achica el JSON)."""
    if isinstance(valor, dict):
        return {clave: _a_listas(v, cifras) for clave, v in valor.items()}
    if isinstance(valor, list):
        return [_a_listas(v, cifras) for v in valor]
    if isinstance(valor, np.ndarray) and valor.ndim == 1:
        return [float(f"{x:.{cifras}g}") for x in valor]
    if isinstance(valor, np.ndarray):
        return [_a_listas(fila, cifras) for fila in valor]
    return valor
