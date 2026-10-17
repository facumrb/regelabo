"""
Endpoints de simulación biológica.
"""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from backend.controller.simulacion import SimulationService
from backend.views.dependencias import usuario_actual

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Simulación Biológica"])


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check() -> Dict[str, Any]:
    """Verifica el estado del servicio y la disponibilidad del solver en C."""
    return SimulationService.get_engine_status()


@router.get("/profiles", response_model=List[str], status_code=status.HTTP_200_OK,
            dependencies=[Depends(usuario_actual)])
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
