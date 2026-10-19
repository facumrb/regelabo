"""
Endpoints de simulación biológica.
"""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Path, status

from backend.controller import perfiles
from backend.controller.modelos import PerfilAuditivo
from backend.controller.simulacion import SimulationService
from backend.views.dependencias import usuario_actual

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Simulación Biológica"])


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check() -> Dict[str, Any]:
    """Verifica el estado del servicio y la disponibilidad del solver en C."""
    return SimulationService.get_engine_status()


@router.get("/profiles", response_model=List[PerfilAuditivo], status_code=status.HTTP_200_OK,
            dependencies=[Depends(usuario_actual)])
def list_profiles() -> List[PerfilAuditivo]:
    """Perfiles de pérdida auditiva base, sin duplicados, con su etiqueta y sus curvas."""
    try:
        return perfiles.listar()
    except Exception as e:
        logger.error(f"Error listando perfiles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"No se pudieron cargar los perfiles de audición: {str(e)}"
        )


@router.get("/profiles/{nombre}", response_model=PerfilAuditivo, status_code=status.HTTP_200_OK,
            dependencies=[Depends(usuario_actual)])
def ver_perfil(nombre: str = Path(pattern=r"^[A-Za-z0-9_-]+$", max_length=100)) -> PerfilAuditivo:
    """Un perfil, base o personalizado: lo usa el detalle de una simulación para mostrar sus curvas."""
    return perfiles.ver(nombre)
