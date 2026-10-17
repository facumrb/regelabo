"""Casos de estudio contra la API y PostgreSQL: CRUD, paginación por cursor y RN4."""

import pytest
from fastapi.testclient import TestClient

from backend.views import crear_app

CASO = {"alias": "Caso 1 – Trauma leve", "edad": 25, "sexo": "femenino", "notas": "Exposición a ruido"}


def _conectado(email, registro_valido):
    """Un navegador nuevo, con un usuario registrado y la sesión iniciada."""
    cliente = TestClient(crear_app())
    cliente.post("/api/auth/registro", json={**registro_valido, "email": email})
    cliente.post("/api/auth/login", json={"email": email, "password": registro_valido["password"]})
    return cliente


@pytest.fixture
def ana(registro_valido):
    return _conectado("ana@example.com", registro_valido)


@pytest.fixture
def beto(registro_valido):
    return _conectado("beto@example.com", registro_valido)


def test_crear_y_ver_un_caso(ana):
    creado = ana.post("/api/casos", json=CASO)
    assert creado.status_code == 201
    assert {k: creado.json()[k] for k in CASO} == CASO
    assert ana.get(f"/api/casos/{creado.json()['id']}").json() == creado.json()


def test_solo_el_alias_es_obligatorio(ana):
    creado = ana.post("/api/casos", json={"alias": "Mínimo"}).json()
    assert creado["edad"] is None and creado["sexo"] is None and creado["notas"] is None


@pytest.mark.parametrize("cambio", [
    {"alias": ""},
    {"alias": "x" * 101},
    {"edad": -1},
    {"edad": 121},
    {"sexo": "F"},
    {"notas": "x" * 2001},
])
def test_datos_invalidos_dan_422(ana, cambio):
    assert ana.post("/api/casos", json={**CASO, **cambio}).status_code == 422


def test_editar_reemplaza_los_datos(ana):
    caso_id = ana.post("/api/casos", json=CASO).json()["id"]
    editado = ana.put(f"/api/casos/{caso_id}", json={"alias": "Renombrado"})
    assert editado.status_code == 200
    assert editado.json()["alias"] == "Renombrado" and editado.json()["edad"] is None


def test_borrar_lo_oculta_de_todo(ana):
    caso_id = ana.post("/api/casos", json=CASO).json()["id"]
    assert ana.delete(f"/api/casos/{caso_id}").status_code == 204
    assert ana.get(f"/api/casos/{caso_id}").status_code == 404
    assert ana.put(f"/api/casos/{caso_id}", json=CASO).status_code == 404
    assert ana.delete(f"/api/casos/{caso_id}").status_code == 404
    assert ana.get("/api/casos").json()["casos"] == []


def test_listado_del_mas_nuevo_al_mas_viejo(ana):
    for i in range(3):
        ana.post("/api/casos", json={"alias": f"Caso {i}"})
    pagina = ana.get("/api/casos").json()
    assert [c["alias"] for c in pagina["casos"]] == ["Caso 2", "Caso 1", "Caso 0"]
    assert pagina["siguiente"] is None


def test_paginacion_por_cursor_sin_repetir_ni_saltear(ana):
    for i in range(25):
        ana.post("/api/casos", json={"alias": f"Caso {i}"})
    vistos, cursor, paginas = [], None, 0
    while True:
        params = {"limite": 10} | ({"despues_de": cursor} if cursor else {})
        pagina = ana.get("/api/casos", params=params).json()
        vistos += [c["alias"] for c in pagina["casos"]]
        paginas += 1
        cursor = pagina["siguiente"]
        if cursor is None:
            break
    assert paginas == 3
    assert vistos == [f"Caso {i}" for i in reversed(range(25))]


def test_pagina_justa_no_ofrece_siguiente(ana):
    for i in range(10):
        ana.post("/api/casos", json={"alias": f"Caso {i}"})
    assert ana.get("/api/casos", params={"limite": 10}).json()["siguiente"] is None


@pytest.mark.parametrize("limite", [0, 101])
def test_limite_fuera_de_rango_da_422(ana, limite):
    assert ana.get("/api/casos", params={"limite": limite}).status_code == 422


def test_rn4_un_caso_ajeno_no_existe(ana, beto):
    caso_id = ana.post("/api/casos", json=CASO).json()["id"]
    assert beto.get(f"/api/casos/{caso_id}").status_code == 404
    assert beto.put(f"/api/casos/{caso_id}", json={"alias": "robado"}).status_code == 404
    assert beto.delete(f"/api/casos/{caso_id}").status_code == 404
    assert beto.get("/api/casos").json()["casos"] == []
    # y el caso de Ana sigue intacto
    assert ana.get(f"/api/casos/{caso_id}").json()["alias"] == CASO["alias"]


def test_rn4_responde_igual_que_un_id_inexistente(ana, beto):
    caso_id = ana.post("/api/casos", json=CASO).json()["id"]
    ajeno = beto.get(f"/api/casos/{caso_id}")
    inexistente = beto.get("/api/casos/00000000-0000-7000-8000-000000000000")
    assert ajeno.status_code == inexistente.status_code == 404
    assert ajeno.json() == inexistente.json()
    assert ajeno.json()["detail"]["codigo"] == "caso_no_encontrado"


def test_sin_sesion_da_401(cliente):
    assert cliente.get("/api/casos").status_code == 401
    assert cliente.post("/api/casos", json=CASO).status_code == 401
