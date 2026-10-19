"""
Punto de entrada de regelabo (Laboratorio Virtual Auditivo).

Desarrollo:  uv run fastapi dev app.py
Producción:  uv run fastapi run app.py
"""

from backend.views import crear_app

app = crear_app()
