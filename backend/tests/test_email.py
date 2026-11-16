"""
Verificación del email (RN15) y recuperación de la contraseña (RN16), decisión 030.
Los mails no se envían: se capturan para leer el enlace.
"""

import re

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from backend.controller import autenticacion
from backend.datos.conexion import engine
from backend.views import crear_app


@pytest.fixture
def buzon(monkeypatch):
    """Lista de (email, token) de cada mail enviado; el envío se hace en el momento, sin hilo."""
    enviados = []
    monkeypatch.setattr(autenticacion, "_en_segundo_plano", lambda enviar, email, token: enviar(email, token))
    monkeypatch.setattr(autenticacion.correo, "enviar",
                        lambda email, asunto, texto: enviados.append(
                            (email, re.search(r"token=([\w-]+)", texto).group(1))))
    return enviados


def _sql(consulta, **parametros):
    with engine.begin() as conexion:
        return conexion.execute(text(consulta), parametros)


def _conectado(cliente, registro_valido):
    cliente.post("/api/auth/registro", json=registro_valido)
    cliente.post("/api/auth/login", json={"email": registro_valido["email"],
                                          "password": registro_valido["password"]})
    return cliente


# ---- RN15: verificación ----

def test_registrarse_manda_el_mail_y_sin_verificar_no_se_puede_simular(cliente, registro_valido, buzon):
    _conectado(cliente, registro_valido)
    assert [email for email, _ in buzon] == ["ana@example.com"]
    assert cliente.get("/api/auth/yo").json()["email_verificado"] is False
    respuesta = cliente.post("/api/simulaciones", json={})
    assert respuesta.status_code == 403 and respuesta.json()["detail"]["codigo"] == "email_no_verificado"


def test_el_enlace_verifica_y_sirve_una_sola_vez(cliente, registro_valido, buzon):
    _conectado(cliente, registro_valido)
    token = buzon[0][1]
    assert token not in _sql("SELECT token_hash FROM enlace_email").scalar()  # solo el hash
    assert cliente.post("/api/auth/verificar", json={"token": token}).status_code == 204
    assert cliente.get("/api/auth/yo").json()["email_verificado"] is True
    otra_vez = cliente.post("/api/auth/verificar", json={"token": token})
    assert otra_vez.status_code == 400 and otra_vez.json()["detail"]["codigo"] == "enlace_invalido"


def test_un_enlace_vencido_no_sirve(cliente, registro_valido, buzon):
    _conectado(cliente, registro_valido)
    _sql("UPDATE enlace_email SET expira_en = now() - interval '1 minute'")
    assert cliente.post("/api/auth/verificar", json={"token": buzon[0][1]}).status_code == 400


def test_reenviar_invalida_el_enlace_anterior(cliente, registro_valido, buzon):
    _conectado(cliente, registro_valido)
    assert cliente.post("/api/auth/reenviar-verificacion").status_code == 204
    viejo, nuevo = buzon[0][1], buzon[1][1]
    assert cliente.post("/api/auth/verificar", json={"token": viejo}).status_code == 400
    assert cliente.post("/api/auth/verificar", json={"token": nuevo}).status_code == 204
    assert cliente.post("/api/auth/reenviar-verificacion").status_code == 409  # ya verificado


def test_reenviar_pide_sesion(cliente):
    assert cliente.post("/api/auth/reenviar-verificacion").status_code == 401


# ---- RN16: recuperación ----

def test_olvide_responde_igual_exista_o_no_el_email(cliente, registro_valido, buzon):
    cliente.post("/api/auth/registro", json=registro_valido)
    buzon.clear()
    existe = cliente.post("/api/auth/olvide", json={"email": "ANA@example.com"})
    no_existe = cliente.post("/api/auth/olvide", json={"email": "nadie@example.com"})
    assert existe.status_code == no_existe.status_code == 202
    assert existe.json() == no_existe.json()
    assert [email for email, _ in buzon] == ["ana@example.com"]


def test_recuperar_cambia_la_contrasena_desbloquea_y_cierra_las_sesiones(cliente, registro_valido, buzon):
    _conectado(cliente, registro_valido)
    _sql("UPDATE usuario SET bloqueado_hasta = now() + interval '1 hour'")
    cliente.post("/api/auth/olvide", json={"email": "ana@example.com"})
    token = buzon[-1][1]

    otro = TestClient(crear_app())
    corta = otro.post("/api/auth/recuperar", json={"token": token, "nueva": "corta"})
    assert corta.status_code == 400  # una contraseña inválida no gasta el enlace
    nueva = otro.post("/api/auth/recuperar", json={"token": token, "nueva": "otra-clave-larga"})
    assert nueva.status_code == 204

    assert cliente.get("/api/auth/yo").status_code == 401  # la sesión vieja se cerró
    login = otro.post("/api/auth/login",
                      json={"email": "ana@example.com", "password": "otra-clave-larga"})
    assert login.status_code == 200 and login.json()["email_verificado"] is True
    reusado = otro.post("/api/auth/recuperar", json={"token": token, "nueva": "tercera-clave"})
    assert reusado.status_code == 400


def test_un_enlace_de_verificacion_no_sirve_para_recuperar(cliente, registro_valido, buzon):
    _conectado(cliente, registro_valido)
    respuesta = cliente.post("/api/auth/recuperar", json={"token": buzon[0][1], "nueva": "otra-clave-larga"})
    assert respuesta.status_code == 400


def test_los_admin_quedan_verificados():
    admin, _ = autenticacion.crear_admin("jefa@example.com", "Jefa", "una-clave-larga")
    assert admin.email_verificado
