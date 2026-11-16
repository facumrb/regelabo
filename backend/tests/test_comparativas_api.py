"""Comparativas guardadas (decisión 025) contra la API y PostgreSQL: CRUD, validaciones y RN4."""

import pytest
from fastapi.testclient import TestClient

from backend.controller import simulaciones
from backend.controller.simulacion import SimulationService
from backend.tests.test_simulaciones import RESPUESTA_FALSA, _conectado
from backend.views import crear_app


@pytest.fixture(autouse=True)
def motor_falso(monkeypatch):
    monkeypatch.setattr(SimulationService, "execute_simulation", staticmethod(lambda _: RESPUESTA_FALSA))


@pytest.fixture
def ana(registro_valido):
    return _conectado("ana@example.com", registro_valido, tipo="investigador")


def _terminadas(cliente, cantidad):
    """Simulaciones distintas del cliente, ya completadas por el worker."""
    ids = []
    for nivel in range(50, 50 + cantidad):
        ids.append(cliente.post("/api/simulaciones", json={"spl_level": nivel}).json()["id"])
        simulaciones.procesar_siguiente()
    return ids


def _guardar(cliente, ids, **extra):
    datos = {"titulo": "Sordera oculta", "simulacion_ids": ids, **extra}
    return cliente.post("/api/comparativas", json=datos)


def test_guardar_y_ver_conserva_el_orden(ana):
    ids = _terminadas(ana, 3)
    creada = _guardar(ana, list(reversed(ids)), notas="Mismas fibras")
    assert creada.status_code == 201
    assert creada.json()["simulacion_ids"] == list(reversed(ids))
    assert ana.get(f"/api/comparativas/{creada.json()['id']}").json() == creada.json()


@pytest.mark.parametrize("cantidad", [1, 5])
def test_entre_2_y_4_simulaciones(ana, cantidad):
    ids = _terminadas(ana, 1) * cantidad
    assert _guardar(ana, ids).status_code == 422


def test_sin_repetir(ana):
    [una, otra] = _terminadas(ana, 2)
    assert _guardar(ana, [una, otra, una]).json()["detail"]["codigo"] == "simulaciones_repetidas"


def test_solo_terminadas(ana):
    [terminada] = _terminadas(ana, 1)
    en_cola = ana.post("/api/simulaciones", json={"spl_level": 90}).json()["id"]
    assert _guardar(ana, [terminada, en_cola]).json()["detail"]["codigo"] == "simulacion_sin_terminar"


def test_ligada_a_un_caso_y_filtrada(ana):
    caso = ana.post("/api/casos", json={"alias": "Caso 1"}).json()["id"]
    ids = _terminadas(ana, 2)
    _guardar(ana, ids, caso_id=caso)
    _guardar(ana, ids, titulo="Sin caso")
    todas = ana.get("/api/comparativas").json()["comparativas"]
    del_caso = ana.get("/api/comparativas", params={"caso_id": caso}).json()["comparativas"]
    assert [c["titulo"] for c in todas] == ["Sin caso", "Sordera oculta"]
    assert [c["caso_id"] for c in del_caso] == [caso]


def test_editar_titulo_notas_y_caso(ana):
    comparativa = _guardar(ana, _terminadas(ana, 2)).json()
    editada = ana.put(f"/api/comparativas/{comparativa['id']}", json={"titulo": "  Nuevo  ", "notas": None})
    assert editada.status_code == 200
    assert editada.json()["titulo"] == "Nuevo"
    assert editada.json()["simulacion_ids"] == comparativa["simulacion_ids"]  # no cambian
    assert ana.put(f"/api/comparativas/{comparativa['id']}", json={"titulo": " "}).status_code == 422


def test_borrar_la_oculta(ana):
    comparativa_id = _guardar(ana, _terminadas(ana, 2)).json()["id"]
    assert ana.delete(f"/api/comparativas/{comparativa_id}").status_code == 204
    assert ana.get(f"/api/comparativas/{comparativa_id}").status_code == 404
    assert ana.get("/api/comparativas").json()["comparativas"] == []


def test_rn4_simulaciones_casos_y_comparativas_ajenas(ana, registro_valido):
    ids = _terminadas(ana, 2)
    comparativa_id = _guardar(ana, ids).json()["id"]
    caso = ana.post("/api/casos", json={"alias": "De Ana"}).json()["id"]
    beto = _conectado("beto@example.com", registro_valido)
    assert _guardar(beto, ids).status_code == 404  # no puede guardar simulaciones de otro
    [suya] = _terminadas(beto, 1)
    assert _guardar(beto, [suya, ids[0]]).status_code == 404
    assert _guardar(beto, _terminadas(beto, 2), caso_id=caso).status_code == 404  # ni ligarla a un caso ajeno
    assert beto.get(f"/api/comparativas/{comparativa_id}").status_code == 404
    assert beto.delete(f"/api/comparativas/{comparativa_id}").status_code == 404
    assert beto.get("/api/comparativas").json()["comparativas"] == []


def test_sin_sesion():
    assert TestClient(crear_app()).get("/api/comparativas").status_code == 401
