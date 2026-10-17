"""
Crea un usuario administrador, o promueve a admin a uno existente.

Uso: uv run python -m backend.comandos.crear_admin
En producción se ejecuta con DATABASE_URL apuntando a la base real.
"""

import sys
from getpass import getpass

from backend.controller.autenticacion import crear_admin
from backend.controller.errores import ErrorDeNegocio


def main() -> int:
    email = input("Email: ").strip()
    nombre = input("Nombre: ").strip() or "Administrador"
    contrasena = getpass("Contraseña (se ignora si el email ya existe): ")
    try:
        usuario, existia = crear_admin(email, nombre, contrasena)
    except ErrorDeNegocio as error:
        print(f"Error: {error.mensaje}")
        return 1
    print(f"{usuario.email} {'promovido a admin' if existia else 'creado como admin'}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
