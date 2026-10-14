"""
Modelos Pydantic para el servicio de simulación biológica (Verhulst 2018).
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    """Parámetros de entrada para ejecutar una simulación del modelo auditivo."""
    
    carrier_freq: float = Field(
        default=4000.0,
        ge=100.0,
        le=12000.0,
        description="Frecuencia portadora del estímulo en Hz (típicamente 500, 1000, 2000, 4000)."
    )
    poles_profile: str = Field(
        default="Flat00",
        description="Perfil de polos de Shera para modelar pérdida auditiva (ej: Flat00, Flat20, Slope20)."
    )
    spl_level: float = Field(
        default=70.0,
        ge=0.0,
        le=120.0,
        description="Nivel de presión sonora del estímulo en dB SPL."
    )
    f_mod: float = Field(
        default=110.0,
        ge=20.0,
        le=500.0,
        description="Frecuencia de modulación del estímulo RAM en Hz (default: 110 Hz)."
    )
    nH: int = Field(
        default=13,
        ge=0,
        le=30,
        description="Fibras HSR (alta tasa espontánea) por IHC. Reducir para simular sinaptopatía."
    )
    nM: int = Field(
        default=3,
        ge=0,
        le=15,
        description="Fibras MSR (media tasa espontánea) por IHC."
    )
    nL: int = Field(
        default=3,
        ge=0,
        le=15,
        description="Fibras LSR (baja tasa espontánea) por IHC."
    )


class SpectrumData(BaseModel):
    """Datos de espectro de frecuencia (FFT) para graficar en Plotly."""
    frequencies: List[float] = Field(description="Frecuencias en Hz (0 a 1000 Hz)")
    amplitudes: List[float] = Field(description="Amplitud de potencia en µV")


class ABRWavesData(BaseModel):
    """Ondas ABR y respuesta temporal para graficar en Plotly."""
    time_ms: List[float] = Field(description="Eje temporal en milisegundos")
    w1: List[float] = Field(description="Onda I: Nervio Auditivo (µV)")
    w3: List[float] = Field(description="Onda III: Núcleo Coclear (µV)")
    w5: List[float] = Field(description="Onda V: Colículo Inferior (µV)")
    efr_wave: List[float] = Field(description="Suma total de ondas ABR (W1+W3+W5) (µV)")


class HarmonicPeak(BaseModel):
    """Detalle de cada armónico analizado para el EFR."""
    harmonic_order: int
    frequency_hz: float
    amplitude_uv: float


class SimulationResponse(BaseModel):
    """Resultados calculados de la simulación biológica."""
    status: str = "success"
    execution_time_seconds: float
    efr_value_uv: float = Field(description="Valor total del biomarcador EFR en microvoltios (µV)")
    harmonics: List[HarmonicPeak]
    fft_spectrum: SpectrumData
    abr_waves: ABRWavesData
    parameters_used: Dict[str, object]
