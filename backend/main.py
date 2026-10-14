"""
Punto de entrada de desarrollo para el backend de regelabo.
Permite ejecutar `uv run fastapi dev main.py` desde `backend/`
y levantar directamente el servicio de simulación con todas sus rutas y documentación OpenAPI.
"""

import os
import sys
import importlib.util

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SIM_SERVICE_DIR = os.path.join(CURRENT_DIR, "services", "simulation-service")

if SIM_SERVICE_DIR not in sys.path:
    sys.path.insert(0, SIM_SERVICE_DIR)

# Cargar la aplicación de simulation-service de forma aislada
_sim_main_path = os.path.join(SIM_SERVICE_DIR, "main.py")
_spec = importlib.util.spec_from_file_location("simulation_service_main", _sim_main_path)
_sim_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_sim_module)

app = _sim_module.app
