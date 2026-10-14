"""
Punto de entrada principal para el microservicio de simulación (simulation-service).
"""

import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Asegurar que el directorio de este servicio y su src estén en el path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from src.api.simulation_controller import router as simulation_router

app = FastAPI(
    title="Laboratorio Virtual Auditivo — Simulation Service",
    description="Microservicio de simulación biofísica auditiva basada en el modelo Verhulst et al. 2018.",
    version="1.0.0"
)

# Configurar CORS para permitir comunicación fluida con el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas
app.include_router(simulation_router)


@app.get("/")
def root():
    return {
        "service": "simulation-service",
        "description": "Motor de Simulación Biológica Verhulst 2018",
        "docs": "/docs"
    }