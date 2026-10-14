"""
Modelos Pydantic para el procesamiento y análisis de audiogramas clínicos.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class AudiogramPoint(BaseModel):
    """Punto de umbral auditivo en una frecuencia específica."""
    frequency: float = Field(ge=100, le=16000, description="Frecuencia en Hz (ej: 250, 500, 1000, 2000, 4000, 8000)")
    hearing_loss_db: float = Field(ge=-10, le=120, description="Pérdida auditiva en dB HL (0 = normal, >25 = pérdida)")


class AudiogramInput(BaseModel):
    """Estructura de entrada manual para un audiograma."""
    patient_name: Optional[str] = Field(default="Paciente", description="Identificador o nombre del paciente")
    points: List[AudiogramPoint] = Field(description="Lista de puntos audiométricos")


class AudiogramResponse(BaseModel):
    """Resultado del análisis del audiograma y su perfil de polos asociado."""
    status: str = "success"
    patient_name: str
    points: List[AudiogramPoint]
    matched_profile: str = Field(description="Perfil de polos de Shera asignado para la simulación")
    mean_hearing_loss: float = Field(description="Pérdida promedio tonal (PTA) en dB HL")
    clinical_classification: str = Field(description="Diagnóstico fonoaudiológico orientativo")
    notes: str = Field(description="Detalles sobre la interpolación coclear")
