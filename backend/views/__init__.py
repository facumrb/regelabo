"""
Capa de presentación HTTP: arma la aplicación FastAPI y registra los routers.

Todas las rutas cuelgan de /api: en desarrollo Vite reenvía /api al backend y en producción
lo hace Caddy, así que el navegador siempre habla con un solo origen (la cookie funciona sin CORS).
"""

from fastapi import Depends, FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from slowapi.errors import RateLimitExceeded

from backend.controller.errores import ErrorDeNegocio
from backend.views import (admin, audiogramas, autenticacion, casos, comentarios, comparativas, simulacion,
                           simulaciones)
from backend.views.dependencias import requiere_admin
from backend.views.errores import manejar_error_de_negocio
from backend.views.limites import demasiados_pedidos, limite_general, limiter


def crear_app() -> FastAPI:
    # Swagger y el esquema OpenAPI solo para admin (decisión 029): se apagan los públicos y se
    # sirven abajo con requiere_admin. La cookie de sesión viaja en /api, así que "Probar" funciona.
    app = FastAPI(
        title="Laboratorio Virtual Auditivo",
        description="Simulación biofísica auditiva basada en el modelo Verhulst et al. 2018.",
        version="0.1.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        dependencies=[Depends(limite_general)],  # 120 pedidos por minuto por sesión (decisión 009)
    )

    @app.get("/api/openapi.json", include_in_schema=False, dependencies=[Depends(requiere_admin)])
    def esquema_openapi():
        return app.openapi()

    @app.get("/api/docs", include_in_schema=False, dependencies=[Depends(requiere_admin)])
    def swagger():
        return get_swagger_ui_html(openapi_url="/api/openapi.json", title=app.title)

    app.state.limiter = limiter
    app.add_exception_handler(ErrorDeNegocio, manejar_error_de_negocio)
    app.add_exception_handler(RateLimitExceeded, demasiados_pedidos)

    app.include_router(autenticacion.router, prefix="/api")
    app.include_router(casos.router, prefix="/api")
    app.include_router(simulacion.router, prefix="/api")
    app.include_router(simulaciones.router, prefix="/api")
    app.include_router(audiogramas.router, prefix="/api")
    app.include_router(comentarios.router, prefix="/api")
    app.include_router(comparativas.router, prefix="/api")
    app.include_router(admin.router, prefix="/api")

    @app.get("/api/")
    def root():
        return {
            "service": "regelabo",
            "description": "Motor de Simulación Biológica Verhulst 2018",
            "docs": "/api/docs",
        }

    return app
