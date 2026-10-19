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

# Simulaciones (RN5). Los cupos son por tipo de perfil.
CUPO_SIMULTANEAS = {"estudiante": 1, "investigador": 3, "fonoaudiologo": 3}
CUPO_POR_HORA = {"estudiante": 10, "investigador": 30, "fonoaudiologo": 30}
TOPE_COLA = int(os.environ.get("TOPE_COLA", 20))
# Una simulación "ejecutando" por más de estos minutos se da por interrumpida (el worker se cayó)
SIMULACION_MINUTOS_MAX = int(os.environ.get("SIMULACION_MINUTOS_MAX", 5))
