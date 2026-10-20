"""
Pone una contraseña nueva a un usuario que la olvidó: también lo desbloquea y cierra todas
sus sesiones. Reemplaza al "olvidé mi contraseña" mientras no haya envío de correos.

Uso: uv run python -m backend.comandos.resetear_contrasena
En producción se ejecuta con DATABASE_URL apuntando a la base real.
"""

import sys
from getpass import getpass

from backend.controller.autenticacion import resetear_contrasena
from backend.controller.errores import ErrorDeNegocio


def main() -> int:
    email = input("Email: ").strip()
    contrasena = getpass("Contraseña nueva: ")
    if getpass("Repetila: ") != contrasena:
        print("Error: las contraseñas no coinciden.")
        return 1
    try:
        usuario = resetear_contrasena(email, contrasena)
    except ErrorDeNegocio as error:
        print(f"Error: {error.mensaje}")
        return 1
    print(f"Contraseña de {usuario.email} cambiada; se cerraron todas sus sesiones.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
