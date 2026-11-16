"""Comentarios (RN13) y su parte del panel de admin (decisión 028), contra la API y PostgreSQL."""

import pytest
from fastapi.testclient import TestClient

from backend.controller import autenticacion
from backend.views import crear_app
from backend.views.limites import limiter


def _conectado(email, registro_valido, tipo="estudiante"):
    cliente = TestClient(crear_app())
    cliente.post("/api/auth/registro", json={**registro_valido, "email": email, "tipo_perfil": tipo})
    cliente.post("/api/auth/login", json={"email": email, "password": registro_valido["password"]})
    return cliente


@pytest.fixture
def ana(registro_valido):
    return _conectado("ana@example.com", registro_valido)


@pytest.fixture
def admin():
    autenticacion.crear_admin("jefa@example.com", "Jefa", "clave-del-admin")
    cliente = TestClient(crear_app())
    cliente.post("/api/auth/login", json={"email": "jefa@example.com", "password": "clave-del-admin"})
    return cliente


def _textos(cliente, **filtros):
    return [c["texto"] for c in cliente.get("/api/admin/comentarios", params=filtros).json()["comentarios"]]


def test_el_autor_no_recibe_nada_y_el_admin_lo_ve_con_sus_datos(ana, admin):
    respuesta = ana.post("/api/comentarios", json={"texto": "  Falta una leyenda en el ABR  "})
    assert respuesta.status_code == 204 and respuesta.content == b""
    comentario = admin.get("/api/admin/comentarios").json()["comentarios"][0]
    assert comentario["texto"] == "Falta una leyenda en el ABR"  # sin los espacios de los bordes
    assert comentario["estado"] == "nuevo"
    assert (comentario["autor_nombre"], comentario["autor_tipo"]) == ("Ana", "estudiante")


@pytest.mark.parametrize("texto", ["", "   ", "x" * 2001])
def test_texto_vacio_o_largo_da_422(ana, texto):
    assert ana.post("/api/comentarios", json={"texto": texto}).status_code == 422


def test_2000_caracteres_entra(ana):
    assert ana.post("/api/comentarios", json={"texto": "x" * 2000}).status_code == 204


def test_sin_sesion_no_se_puede_comentar(cliente):
    assert cliente.post("/api/comentarios", json={"texto": "Hola"}).status_code == 401


@pytest.mark.parametrize("pedido", [
    ("get", "/api/admin/comentarios"),
    ("get", "/api/admin/pendientes"),
    ("patch", "/api/admin/comentarios/0190a000-0000-7000-8000-000000000000"),
])
def test_solo_el_admin_entra_al_panel(ana, cliente, pedido):
    metodo, url = pedido
    assert getattr(ana, metodo)(url).status_code == 403
    assert getattr(cliente, metodo)(url).status_code == 401


def test_estados_libres_y_archivados_ocultos_por_defecto(ana, admin):
    ana.post("/api/comentarios", json={"texto": "Uno"})
    comentario_id = admin.get("/api/admin/comentarios").json()["comentarios"][0]["id"]

    def cambiar(estado):
        return admin.patch(f"/api/admin/comentarios/{comentario_id}", json={"estado": estado})

    assert cambiar("archivado").json()["estado"] == "archivado"
    assert _textos(admin) == []
    assert _textos(admin, estado="archivado") == ["Uno"]
    assert cambiar("nuevo").status_code == 200  # se puede volver atrás
    assert _textos(admin) == ["Uno"]
    assert cambiar("borrado").status_code == 422


def test_comentario_inexistente_da_404(admin):
    respuesta = admin.patch("/api/admin/comentarios/0190a000-0000-7000-8000-000000000000",
                            json={"estado": "leido"})
    assert respuesta.status_code == 404
    assert respuesta.json()["detail"]["codigo"] == "comentario_no_encontrado"


def test_filtro_por_tipo_de_usuario(ana, admin, registro_valido):
    fono = _conectado("fono@example.com", registro_valido, tipo="fonoaudiologo")
    ana.post("/api/comentarios", json={"texto": "De estudiante"})
    fono.post("/api/comentarios", json={"texto": "De fonoaudióloga"})
    assert _textos(admin) == ["De fonoaudióloga", "De estudiante"]
    assert _textos(admin, tipo="fonoaudiologo") == ["De fonoaudióloga"]


def test_paginacion_por_cursor(ana, admin):
    for i in range(5):
        ana.post("/api/comentarios", json={"texto": f"C{i}"})
    primera = admin.get("/api/admin/comentarios", params={"limite": 3}).json()
    cursor = {"limite": 3, "despues_de": primera["siguiente"]}
    segunda = admin.get("/api/admin/comentarios", params=cursor).json()
    textos = [c["texto"] for c in primera["comentarios"] + segunda["comentarios"]]
    assert textos == ["C4", "C3", "C2", "C1", "C0"]
    assert segunda["siguiente"] is None


def test_pendientes_cuenta_solo_los_nuevos(ana, admin):
    for texto in ["A", "B"]:
        ana.post("/api/comentarios", json={"texto": texto})
    assert admin.get("/api/admin/pendientes").json() == {"comentarios_nuevos": 2, "restablecimientos": 0}
    comentario_id = admin.get("/api/admin/comentarios").json()["comentarios"][0]["id"]
    admin.patch(f"/api/admin/comentarios/{comentario_id}", json={"estado": "leido"})
    assert admin.get("/api/admin/pendientes").json() == {"comentarios_nuevos": 1, "restablecimientos": 0}


def test_mas_de_cinco_comentarios_por_minuto_se_limitan(ana, registro_valido):
    limiter.enabled = True
    estados = [ana.post("/api/comentarios", json={"texto": "spam"}).status_code for _ in range(6)]
    assert estados == [204] * 5 + [429]
    # el límite es de cada usuario, no de la IP (todos los tests vienen de la misma)
    otro = _conectado("beto@example.com", registro_valido)
    assert otro.post("/api/comentarios", json={"texto": "hola"}).status_code == 204
