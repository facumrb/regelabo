"""Cambio de contraseña con la sesión iniciada y reseteo por comando del admin."""

import pytest
from fastapi.testclient import TestClient

from backend.controller import autenticacion
from backend.controller.errores import ErrorDeNegocio
from backend.views import crear_app

CLAVE = "una-clave-larga"
NUEVA = "otra-clave-larga"


def _ventana_con_sesion(email="ana@example.com", password=CLAVE):
    cliente = TestClient(crear_app())
    assert cliente.post("/api/auth/login", json={"email": email, "password": password}).status_code == 200
    return cliente


@pytest.fixture
def ana(cliente, registro_valido):
    cliente.post("/api/auth/registro", json=registro_valido)
    return _ventana_con_sesion()


def _cambiar(cliente, actual=CLAVE, nueva=NUEVA):
    return cliente.post("/api/auth/contrasena", json={"actual": actual, "nueva": nueva})


def _login(password):
    datos = {"email": "ana@example.com", "password": password}
    return TestClient(crear_app()).post("/api/auth/login", json=datos)


def test_cambio_exitoso(ana):
    assert _cambiar(ana).status_code == 204
    assert _login(CLAVE).status_code == 401
    assert _login(NUEVA).status_code == 200


def test_cierra_las_demas_sesiones_y_conserva_la_actual(ana):
    celular = _ventana_con_sesion()
    assert _cambiar(ana).status_code == 204
    assert ana.get("/api/auth/yo").status_code == 200
    assert celular.get("/api/auth/yo").status_code == 401


def test_actual_incorrecta(ana):
    respuesta = _cambiar(ana, actual="no-es-esta")
    assert respuesta.status_code == 400
    assert respuesta.json()["detail"]["codigo"] == "contrasena_actual_incorrecta"
    assert _login(CLAVE).status_code == 200  # no cambió nada


def test_actual_incorrecta_suma_fallos_y_bloquea(ana):
    for _ in range(autenticacion.INTENTOS_MAX):
        _cambiar(ana, actual="no-es-esta")
    respuesta = _cambiar(ana)
    assert respuesta.status_code == 429
    assert respuesta.json()["detail"]["codigo"] == "cuenta_bloqueada"
    assert _login(CLAVE).json()["detail"]["codigo"] == "cuenta_bloqueada"


def test_cambio_exitoso_reinicia_los_fallos(ana):
    for _ in range(autenticacion.INTENTOS_MAX - 1):
        _cambiar(ana, actual="no-es-esta")
    assert _cambiar(ana).status_code == 204
    _cambiar(ana, actual="no-es-esta")  # un fallo más: si no se hubiera reiniciado, bloquearía
    assert _login(NUEVA).status_code == 200


@pytest.mark.parametrize("nueva, codigo", [("corta", "contrasena_invalida"), (CLAVE, "contrasena_repetida")])
def test_nueva_invalida(ana, nueva, codigo):
    respuesta = _cambiar(ana, nueva=nueva)
    assert respuesta.status_code == 400
    assert respuesta.json()["detail"]["codigo"] == codigo
    assert _login(CLAVE).status_code == 200


def test_sin_sesion_da_401(cliente):
    assert _cambiar(cliente).status_code == 401


def test_resetear_por_comando(ana):
    for _ in range(autenticacion.INTENTOS_MAX):
        _login("no-es-esta")  # queda bloqueada
    autenticacion.resetear_contrasena("ANA@example.com", NUEVA)
    assert ana.get("/api/auth/yo").status_code == 401  # se cerraron todas, incluida esta
    assert _login(NUEVA).status_code == 200  # y quedó desbloqueada


def test_resetear_email_inexistente():
    with pytest.raises(ErrorDeNegocio) as error:
        autenticacion.resetear_contrasena("nadie@example.com", NUEVA)
    assert error.value.codigo == "usuario_no_encontrado"
