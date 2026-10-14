"""
Endpoints de carga y análisis de audiogramas.
"""

import logging
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from backend.controller.audiogramas import AudiogramService
from backend.controller.modelos import AudiogramInput, AudiogramResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Simulación Biológica"])


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
