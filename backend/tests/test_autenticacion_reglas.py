"""Reglas de negocio de autenticación que no necesitan base de datos."""

import pytest

from backend.controller import autenticacion
from backend.controller.errores import ErrorDeNegocio
from backend.controller.modelos import Usuario
from backend.views.dependencias import requiere_admin


@pytest.mark.parametrize("contrasena", ["", "corta", "a" * 7, "a" * 129])
def test_contrasena_fuera_de_rango_se_rechaza(contrasena):
    with pytest.raises(ErrorDeNegocio) as error:
        autenticacion.validar_contrasena(contrasena)
    assert error.value.codigo == "contrasena_invalida"


@pytest.mark.parametrize("contrasena", ["a" * 8, "a" * 128, "con espacios y ñ ✓"])
def test_contrasena_dentro_de_rango_se_acepta(contrasena):
    autenticacion.validar_contrasena(contrasena)


def _usuario(es_admin):
    return Usuario(id="01a13b85-e446-73d2-a1d2-dfdfd591b098", email="a@b.com", nombre="A",
                   tipo_perfil="estudiante", es_admin=es_admin, password_hash="x",
                   intentos_fallidos=0, bloqueado_hasta=None)


def test_requiere_admin_rechaza_a_un_usuario_comun():
    with pytest.raises(ErrorDeNegocio) as error:
        requiere_admin(_usuario(es_admin=False))
    assert error.value.codigo == "sin_permiso"


def test_requiere_admin_deja_pasar_a_un_admin():
    assert requiere_admin(_usuario(es_admin=True)).es_admin


def test_el_hash_de_la_contrasena_no_sale_al_serializar_el_usuario():
    assert "password_hash" not in _usuario(es_admin=False).model_dump()
