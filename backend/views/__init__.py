"""
Capa de presentación HTTP: arma la aplicación FastAPI y registra los routers.

Todas las rutas cuelgan de /api: en desarrollo Vite reenvía /api al backend y en producción
lo hace Caddy, así que el navegador siempre habla con un solo origen (la cookie funciona sin CORS).
"""

from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded

from backend.controller.errores import ErrorDeNegocio
from backend.views import audiogramas, autenticacion, casos, simulacion, simulaciones
from backend.views.errores import manejar_error_de_negocio
from backend.views.limites import demasiados_pedidos, limiter


def crear_app() -> FastAPI:
    app = FastAPI(
        title="Laboratorio Virtual Auditivo",
        description="Simulación biofísica auditiva basada en el modelo Verhulst et al. 2018.",
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )
    app.state.limiter = limiter
    app.add_exception_handler(ErrorDeNegocio, manejar_error_de_negocio)
    app.add_exception_handler(RateLimitExceeded, demasiados_pedidos)

    app.include_router(autenticacion.router, prefix="/api")
    app.include_router(casos.router, prefix="/api")
    app.include_router(simulacion.router, prefix="/api")
    app.include_router(simulaciones.router, prefix="/api")
    app.include_router(audiogramas.router, prefix="/api")

    @app.get("/api/")
    def root():
        return {
            "service": "regelabo",
            "description": "Motor de Simulación Biológica Verhulst 2018",
            "docs": "/api/docs",
        }

    return app
