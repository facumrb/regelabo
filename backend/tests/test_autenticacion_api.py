"""Registro, login, sesión y logout contra la API y PostgreSQL."""

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import text

from backend.controller import autenticacion
from backend.datos.conexion import engine
from backend.views import crear_app
from backend.views.limites import limiter


def _registrar(cliente, datos):
    return cliente.post("/api/auth/registro", json=datos)


def _login(cliente, email="ana@example.com", password="una-clave-larga"):
    return cliente.post("/api/auth/login", json={"email": email, "password": password})


def _sql(consulta, **parametros):
    with engine.begin() as conexion:
        return conexion.execute(text(consulta), parametros)


def test_registro_crea_el_usuario_sin_exponer_el_hash(cliente, registro_valido):
    respuesta = _registrar(cliente, registro_valido)
    assert respuesta.status_code == 201
    assert respuesta.json().keys() == {"id", "email", "nombre", "tipo_perfil", "es_admin"}
    assert respuesta.json()["es_admin"] is False


def test_el_hash_guardado_no_es_la_contrasena(cliente, registro_valido):
    _registrar(cliente, registro_valido)
    guardado = _sql("SELECT password_hash FROM usuario").scalar()
    assert guardado.startswith("$argon2id$") and registro_valido["password"] not in guardado


def test_registro_sin_aceptar_el_aviso_se_rechaza(cliente, registro_valido):
    respuesta = _registrar(cliente, {**registro_valido, "acepta_aviso": False})
    assert respuesta.status_code == 400
    assert respuesta.json()["detail"]["codigo"] == "aviso_no_aceptado"


def test_registro_con_contrasena_corta_se_rechaza(cliente, registro_valido):
    respuesta = _registrar(cliente, {**registro_valido, "password": "corta"})
    assert respuesta.status_code == 400
    assert respuesta.json()["detail"]["codigo"] == "contrasena_invalida"


def test_registro_con_email_invalido_devuelve_422(cliente, registro_valido):
    assert _registrar(cliente, {**registro_valido, "email": "no-es-un-email"}).status_code == 422


def test_email_duplicado_se_rechaza_sin_importar_mayusculas(cliente, registro_valido):
    _registrar(cliente, registro_valido)
    respuesta = _registrar(cliente, {**registro_valido, "email": "ANA@Example.com"})
    assert respuesta.status_code == 409
    assert respuesta.json()["detail"]["codigo"] == "email_ya_registrado"


def test_login_deja_una_cookie_httponly_y_yo_devuelve_al_usuario(cliente, registro_valido):
    _registrar(cliente, registro_valido)
    respuesta = _login(cliente)
    assert respuesta.status_code == 200
    cookie = respuesta.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=lax" in cookie and "path=/api" in cookie
    assert cliente.get("/api/auth/yo").json()["email"] == "ana@example.com"


def test_el_token_no_se_guarda_en_claro(cliente, registro_valido):
    _registrar(cliente, registro_valido)
    token = _login(cliente).cookies["sesion"]
    assert token not in _sql("SELECT token_hash FROM sesion").scalar()


def test_sin_sesion_yo_devuelve_401(cliente):
    respuesta = cliente.get("/api/auth/yo")
    assert respuesta.status_code == 401
    assert respuesta.json()["detail"]["codigo"] == "no_autenticado"


def test_credenciales_incorrectas_dan_la_misma_respuesta_exista_o_no_el_email(cliente, registro_valido):
    _registrar(cliente, registro_valido)
    clave_mala = _login(cliente, password="otra-clave-larga")
    sin_cuenta = _login(cliente, email="nadie@example.com")
    assert clave_mala.status_code == sin_cuenta.status_code == 401
    assert clave_mala.json() == sin_cuenta.json()


def test_diez_fallos_seguidos_bloquean_la_cuenta_aunque_la_clave_sea_correcta(cliente, registro_valido):
    _registrar(cliente, registro_valido)
    for _ in range(10):
        assert _login(cliente, password="incorrecta-123").status_code == 401
    bloqueada = _login(cliente)
    assert bloqueada.status_code == 429
    assert bloqueada.json()["detail"]["codigo"] == "cuenta_bloqueada"


def test_pasado_el_bloqueo_se_puede_entrar_y_el_contador_se_reinicia(cliente, registro_valido):
    _registrar(cliente, registro_valido)
    for _ in range(10):
        _login(cliente, password="incorrecta-123")
    _sql("UPDATE usuario SET bloqueado_hasta = :t", t=datetime.now(timezone.utc) - timedelta(minutes=1))
    assert _login(cliente).status_code == 200
    assert _sql("SELECT intentos_fallidos, bloqueado_hasta FROM usuario").one() == (0, None)


def test_un_fallo_aislado_no_bloquea_y_un_login_correcto_reinicia_el_contador(cliente, registro_valido):
    _registrar(cliente, registro_valido)
    _login(cliente, password="incorrecta-123")
    assert _sql("SELECT intentos_fallidos FROM usuario").scalar() == 1
    assert _login(cliente).status_code == 200
    assert _sql("SELECT intentos_fallidos FROM usuario").scalar() == 0


def test_logout_invalida_el_token_en_el_servidor(cliente, registro_valido):
    _registrar(cliente, registro_valido)
    token = _login(cliente).cookies["sesion"]
    assert cliente.post("/api/auth/logout").status_code == 204
    # Un token copiado antes del logout ya no sirve, aunque alguien lo conserve
    copia = TestClient(crear_app(), cookies={"sesion": token})
    assert copia.get("/api/auth/yo").status_code == 401


def test_una_sesion_vencida_no_sirve(cliente, registro_valido):
    _registrar(cliente, registro_valido)
    _login(cliente)
    _sql("UPDATE sesion SET expira_en = :t", t=datetime.now(timezone.utc) - timedelta(seconds=1))
    assert cliente.get("/api/auth/yo").status_code == 401


def test_dos_ventanas_son_independientes(registro_valido):
    normal, incognito = TestClient(crear_app()), TestClient(crear_app())
    _registrar(normal, registro_valido)
    _registrar(normal, {**registro_valido, "email": "beto@example.com", "nombre": "Beto"})
    _login(normal)
    assert incognito.get("/api/auth/yo").status_code == 401
    _login(incognito, email="beto@example.com")
    assert normal.get("/api/auth/yo").json()["nombre"] == "Ana"
    assert incognito.get("/api/auth/yo").json()["nombre"] == "Beto"


def test_el_login_borra_las_sesiones_vencidas(cliente, registro_valido):
    _registrar(cliente, registro_valido)
    _login(cliente)
    _sql("UPDATE sesion SET expira_en = :t", t=datetime.now(timezone.utc) - timedelta(hours=1))
    _login(cliente)
    assert _sql("SELECT count(*) FROM sesion").scalar() == 1


def test_mas_de_cinco_intentos_por_minuto_se_limitan(cliente, registro_valido):
    limiter.enabled = True
    estados = [_login(cliente, password="incorrecta-123").status_code for _ in range(6)]
    assert estados == [401] * 5 + [429]


def test_crear_admin_y_promover_a_un_usuario_existente(cliente, registro_valido):
    usuario, existia = autenticacion.crear_admin("Jefe@Example.com", "Jefe", "clave-del-admin")
    assert existia is False and usuario.es_admin
    assert _login(cliente, email="jefe@example.com", password="clave-del-admin").json()["es_admin"] is True

    _registrar(cliente, registro_valido)
    _, existia = autenticacion.crear_admin("ana@example.com", "Ana", "clave-del-admin")
    assert existia is True
    assert _sql("SELECT es_admin FROM usuario WHERE email = 'ana@example.com'").scalar() is True
