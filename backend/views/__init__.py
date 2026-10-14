"""
Capa de presentación HTTP: arma la aplicación FastAPI y registra los routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.views import audiogramas, simulacion


def crear_app() -> FastAPI:
    app = FastAPI(
        title="Laboratorio Virtual Auditivo",
        description="Simulación biofísica auditiva basada en el modelo Verhulst et al. 2018.",
        version="0.1.0",
    )

    # Configurar CORS para permitir comunicación fluida con el frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(simulacion.router)
    app.include_router(audiogramas.router)

    @app.get("/")
    def root():
        return {
            "service": "regelabo",
            "description": "Motor de Simulación Biológica Verhulst 2018",
            "docs": "/docs",
        }

    return app
