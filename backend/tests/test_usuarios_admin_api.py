"""Usuarios en el panel de admin (decisión 028, etapa 3), contra la API y PostgreSQL."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from backend.controller import autenticacion
from backend.datos.conexion import engine
from backend.services import correo
from backend.views import crear_app

INEXISTENTE = "0190a000-0000-7000-8000-000000000000"


def _sql(consulta):
    with engine.begin() as conexion:
        return conexion.execute(text(consulta))


def _conectado(email, password):
    cliente = TestClient(crear_app())
    cliente.post("/api/auth/login", json={"email": email, "password": password})
    return cliente


@pytest.fixture
def ana(registro_valido):
    """Una estudiante registrada (sin verificar), con la sesión iniciada."""
    cliente = TestClient(crear_app())
    cliente.post("/api/auth/registro", json=registro_valido)
    cliente.post("/api/auth/login", json={"email": "ana@example.com",
                                          "password": registro_valido["password"]})
    return cliente


@pytest.fixture
def admin():
    autenticacion.crear_admin("jefa@example.com", "Jefa", "clave-del-admin")
    return _conectado("jefa@example.com", "clave-del-admin")


def _usuario(admin, email):
    lista = admin.get("/api/admin/usuarios", params={"busqueda": email}).json()["usuarios"]
    return next(u for u in lista if u["email"] == email)


def test_lista_con_totales_sin_contenido(ana, admin):
    ana.post("/api/casos", json={"alias": "Uno"})
    caso_id = ana.post("/api/casos", json={"alias": "Borrado"}).json()["id"]
    ana.delete(f"/api/casos/{caso_id}")
    fila = _usuario(admin, "ana@example.com")
    assert fila["casos"] == 1 and fila["simulaciones"] == 0  # el borrado no cuenta
    assert fila["email_verificado"] is False and fila["bloqueado_hasta"] is None
    assert "password_hash" not in fila and "alias" not in str(fila)


def _lista(admin, **filtros):
    return admin.get("/api/admin/usuarios", params=filtros).json()["usuarios"]


def test_busqueda_por_parte_del_email_o_del_nombre(ana, admin):
    assert [u["email"] for u in _lista(admin, busqueda="ANA@")] == ["ana@example.com"]
    assert [u["nombre"] for u in _lista(admin, busqueda="jef")] == ["Jefa"]
    assert _lista(admin, busqueda="%") == []  # los comodines de LIKE se buscan como texto


def test_filtro_por_tipo(ana, admin):
    assert {u["tipo_perfil"] for u in _lista(admin, tipo="estudiante")} == {"estudiante"}


def test_verificar_el_email_a_mano_habilita_a_simular(ana, admin):
    ana_id = _usuario(admin, "ana@example.com")["id"]
    respuesta = admin.post(f"/api/admin/usuarios/{ana_id}/verificar-email")
    assert respuesta.status_code == 200 and respuesta.json()["email_verificado"] is True
    assert ana.get("/api/auth/yo").json()["email_verificado"] is True
    assert admin.post(f"/api/admin/usuarios/{ana_id}/verificar-email").status_code == 200  # de nuevo: igual


def test_desbloquear(ana, admin, registro_valido):
    _sql("UPDATE usuario SET bloqueado_hasta = now() + interval '15 minutes', intentos_fallidos = 3 "
         "WHERE email = 'ana@example.com'")
    assert _conectado("ana@example.com", registro_valido["password"]).get("/api/auth/yo").status_code == 401
    ana_id = _usuario(admin, "ana@example.com")["id"]
    assert admin.post(f"/api/admin/usuarios/{ana_id}/desbloquear").json()["bloqueado_hasta"] is None
    assert _conectado("ana@example.com", registro_valido["password"]).get("/api/auth/yo").status_code == 200


def _pedir(email="ana@example.com"):
    return TestClient(crear_app()).post("/api/auth/olvide", json={"email": email})


def test_el_pedido_aparece_en_el_panel_y_en_el_contador(ana, admin):
    assert admin.get("/api/admin/pendientes").json()["restablecimientos"] == 0
    assert _pedir().status_code == 202
    assert _pedir("nadie@example.com").status_code == 202  # misma respuesta, sin pedido (RN16)
    assert admin.get("/api/admin/pendientes").json()["restablecimientos"] == 1
    assert [u["email"] for u in _lista(admin, con_pedido=True)] == ["ana@example.com"]
    assert _usuario(admin, "ana@example.com")["restablecimiento_pedido_en"] is not None


def test_con_smtp_el_pedido_llega_al_admin_solo_si_el_usuario_avisa(ana, admin, monkeypatch):
    monkeypatch.setattr(correo, "SMTP_HOST", "smtp.example.com")
    monkeypatch.setattr(autenticacion, "_en_segundo_plano", lambda *_: None)  # sin mandar nada de verdad
    _pedir()
    assert admin.get("/api/admin/pendientes").json()["restablecimientos"] == 0  # alcanza con el enlace
    avisar = TestClient(crear_app()).post
    assert avisar("/api/auth/olvide/avisar-admin", json={"email": "nadie@example.com"}).status_code == 202
    assert avisar("/api/auth/olvide/avisar-admin", json={"email": "Ana@Example.com"}).status_code == 202
    assert [u["email"] for u in _lista(admin, con_pedido=True)] == ["ana@example.com"]


def test_sin_pedido_no_hay_contrasena_temporal(ana, admin):
    ana_id = _usuario(admin, "ana@example.com")["id"]
    respuesta = admin.post(f"/api/admin/usuarios/{ana_id}/resetear-contrasena")
    assert respuesta.status_code == 409
    assert respuesta.json()["detail"]["codigo"] == "sin_pedido_de_restablecimiento"


def test_cambiar_la_contrasena_atiende_el_pedido(ana, admin, registro_valido):
    _pedir()
    cambio = {"actual": registro_valido["password"], "nueva": "otra-clave-larga"}
    assert ana.post("/api/auth/contrasena", json=cambio).status_code == 204
    assert admin.get("/api/admin/pendientes").json()["restablecimientos"] == 0


def test_contrasena_temporal_cierra_las_sesiones(ana, admin, registro_valido):
    _pedir()
    ana_id = _usuario(admin, "ana@example.com")["id"]
    temporal = admin.post(f"/api/admin/usuarios/{ana_id}/resetear-contrasena").json()["contrasena_temporal"]
    assert len(temporal) >= 16
    assert ana.get("/api/auth/yo").status_code == 401  # su sesión se cerró
    assert _conectado("ana@example.com", registro_valido["password"]).get("/api/auth/yo").status_code == 401
    assert _conectado("ana@example.com", temporal).get("/api/auth/yo").status_code == 200
    assert admin.get("/api/admin/pendientes").json()["restablecimientos"] == 0  # pedido atendido


@pytest.mark.parametrize("accion", ["desbloquear", "verificar-email", "resetear-contrasena"])
def test_nada_se_aplica_a_otro_admin(admin, accion):
    otro, _ = autenticacion.crear_admin("otro@example.com", "Otro", "clave-del-admin")
    respuesta = admin.post(f"/api/admin/usuarios/{otro.id}/{accion}")
    assert respuesta.status_code == 403 and respuesta.json()["detail"]["codigo"] == "usuario_es_admin"
    assert _conectado("otro@example.com", "clave-del-admin").get("/api/auth/yo").status_code == 200


@pytest.mark.parametrize("accion", ["desbloquear", "verificar-email", "resetear-contrasena"])
def test_usuario_inexistente_da_404(admin, accion):
    assert admin.post(f"/api/admin/usuarios/{INEXISTENTE}/{accion}").status_code == 404


def test_solo_el_admin_ve_y_toca_usuarios(ana, cliente):
    assert ana.get("/api/admin/usuarios").status_code == 403
    assert ana.post(f"/api/admin/usuarios/{INEXISTENTE}/desbloquear").status_code == 403
    assert cliente.get("/api/admin/usuarios").status_code == 401


# ---- Cambio obligatorio después de una contraseña temporal (decisión 031) ----

def _con_temporal(admin):
    """Ana pidió restablecer, el admin le generó una temporal y ella entró con esa."""
    _pedir()
    ana_id = _usuario(admin, "ana@example.com")["id"]
    temporal = admin.post(f"/api/admin/usuarios/{ana_id}/resetear-contrasena").json()["contrasena_temporal"]
    return _conectado("ana@example.com", temporal), temporal


def test_con_la_temporal_solo_puede_elegir_una_nueva(ana, admin):
    cliente, _ = _con_temporal(admin)
    assert cliente.get("/api/auth/yo").json()["debe_cambiar_contrasena"] is True
    pedidos = [cliente.get("/api/casos"), cliente.get("/api/simulaciones"),
               cliente.post("/api/comentarios", json={"texto": "x"})]
    for respuesta in pedidos:
        assert respuesta.status_code == 403
        assert respuesta.json()["detail"]["codigo"] == "debe_cambiar_contrasena"


def test_elegir_la_nueva_sin_la_actual_libera_la_cuenta(ana, admin):
    cliente, temporal = _con_temporal(admin)
    elegir = cliente.post
    assert elegir("/api/auth/contrasena-temporal", json={"nueva": temporal}).status_code == 400  # repetida
    assert cliente.post("/api/auth/contrasena-temporal", json={"nueva": "corta"}).status_code == 400
    assert cliente.post("/api/auth/contrasena-temporal", json={"nueva": "mi-clave-nueva"}).status_code == 204
    assert cliente.get("/api/auth/yo").json()["debe_cambiar_contrasena"] is False  # la sesión sigue
    assert cliente.get("/api/casos").status_code == 200
    assert _conectado("ana@example.com", temporal).get("/api/auth/yo").status_code == 401
    assert _conectado("ana@example.com", "mi-clave-nueva").get("/api/auth/yo").status_code == 200


def test_sin_temporal_no_se_puede_saltear_la_actual(ana):
    respuesta = ana.post("/api/auth/contrasena-temporal", json={"nueva": "otra-clave-larga"})
    assert respuesta.status_code == 409 and respuesta.json()["detail"]["codigo"] == "sin_contrasena_temporal"


def test_el_comando_tambien_obliga_a_cambiarla(ana):
    autenticacion.resetear_contrasena("ana@example.com", "clave-del-comando")
    cliente = _conectado("ana@example.com", "clave-del-comando")
    assert cliente.get("/api/casos").json()["detail"]["codigo"] == "debe_cambiar_contrasena"
