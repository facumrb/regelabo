"""
Parámetros configurables del sistema.

Se leen de variables de entorno; en desarrollo, del archivo `.env` de la raíz (ver `.env.example`).
"""

import os

from dotenv import load_dotenv

# Ruta explícita: la búsqueda automática de python-dotenv falla cuando Alembic carga este módulo
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

DATABASE_URL = os.environ["DATABASE_URL"]

# Sesiones y bloqueo de cuentas
SESION_HORAS = int(os.environ.get("SESION_HORAS", 12))
INTENTOS_MAX = int(os.environ.get("INTENTOS_MAX", 10))
BLOQUEO_MINUTOS = int(os.environ.get("BLOQUEO_MINUTOS", 15))

# La cookie de sesión solo viaja por HTTPS; en desarrollo (http) se desactiva en el .env
COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "true").lower() == "true"
