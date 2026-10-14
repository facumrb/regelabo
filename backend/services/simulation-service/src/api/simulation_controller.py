"""
Controlador FastAPI para endpoints de simulación biológica.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
import logging

from src.models.simulation_model import SimulationRequest, SimulationResponse
from src.models.audiogram_model import AudiogramInput, AudiogramResponse
from src.services.simulation_service import SimulationService
from src.services.audiogram_service import AudiogramService

# Configurar logger
logger = logging.getLogger("simulation_controller")
router = APIRouter(tags=["Simulación Biológica"])


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check() -> Dict[str, Any]:
    """Verifica el estado del servicio y la disponibilidad del solver en C."""
    try:
        from core.cochlear_model2018 import HAS_CLIB
    except Exception:
        HAS_CLIB = False

    return {
        "status": "online",
        "service": "simulation-service",
        "c_solver_available": HAS_CLIB
    }


@router.get("/profiles", response_model=List[str], status_code=status.HTTP_200_OK)
def list_profiles() -> List[str]:
    """Retorna la lista de todos los perfiles de pérdida auditiva (polos de Shera) disponibles."""
    try:
        return SimulationService.list_available_profiles()
    except Exception as e:
        logger.error(f"Error listando perfiles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"No se pudieron cargar los perfiles de audición: {str(e)}"
        )


@router.post("/simulate", response_model=SimulationResponse, status_code=status.HTTP_200_OK)
def simulate(request: SimulationRequest) -> SimulationResponse:
    """
    Ejecuta el modelo Verhulst 2018 para los parámetros provistos.
    Devuelve los datos de EFR, armónicos, espectro FFT y ondas ABR para visualización.
    """
    try:
        result = SimulationService.execute_simulation(request)
        return result
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error en la simulación: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante el cálculo de simulación: {str(e)}"
        )


@router.post("/audiogram/upload", response_model=AudiogramResponse, status_code=status.HTTP_200_OK)
async def upload_audiogram(
    file: UploadFile = File(...),
    patient_name: Optional[str] = Form("Paciente")
) -> AudiogramResponse:
    """
    Recibe un archivo de audiograma (CSV/TXT) vía FilePond,
    extrae los umbrales de audición y genera el perfil coclear correspondiente.
    """
    try:
        content_bytes = await file.read()
        content_str = content_bytes.decode("utf-8", errors="replace")
        points = AudiogramService.parse_file_content(content_str)
        return AudiogramService.analyze_and_map(patient_name=patient_name or "Paciente", points=points)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Error procesando audiograma: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando el archivo: {str(e)}"
        )


@router.post("/audiogram/manual", response_model=AudiogramResponse, status_code=status.HTTP_200_OK)
def manual_audiogram(input_data: AudiogramInput) -> AudiogramResponse:
    """
    Recibe los puntos del audiograma directamente en formato JSON (para carga interactiva).
    """
    try:
        return AudiogramService.analyze_and_map(
            patient_name=input_data.patient_name or "Paciente",
            points=input_data.points
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Error analizando audiograma manual: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en el análisis del audiograma: {str(e)}"
        )

