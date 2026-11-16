"""Audiogramas guardados en un caso (decisión 032), contra la API y PostgreSQL."""

import pytest
from fastapi.testclient import TestClient

from backend.views import crear_app

PUNTOS = [{"frequency": f, "hearing_loss_db": db}
          for f, db in [(250, 10), (500, 15), (1000, 20), (2000, 40), (4000, 60), (8000, 70)]]


def _conectado(email, registro_valido):
    cliente = TestClient(crear_app())
    cliente.post("/api/auth/registro", json={**registro_valido, "email": email})
    cliente.post("/api/auth/login", json={"email": email, "password": registro_valido["password"]})
    return cliente


@pytest.fixture
def ana(registro_valido):
    return _conectado("ana@example.com", registro_valido)


@pytest.fixture
def caso_de_ana(ana):
    return ana.post("/api/casos", json={"alias": "Caso ruido"}).json()["id"]


def _cargar(cliente, caso_id=None, puntos=PUNTOS):
    return cliente.post("/api/audiogram/manual", json={"patient_name": "Nombre a mano", "points": puntos,
                                                       "caso_id": caso_id})


def test_se_guarda_en_el_caso_con_la_clasificacion_de_rn2(ana, caso_de_ana):
    respuesta = _cargar(ana, caso_de_ana)
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["audiograma_id"] is not None
    assert cuerpo["patient_name"] == "Caso ruido"  # toma el alias del caso, no el nombre escrito
    [guardado] = ana.get(f"/api/casos/{caso_de_ana}/audiogramas").json()
    assert guardado["id"] == cuerpo["audiograma_id"] and guardado["perfil"] == cuerpo["matched_profile"]
    clasificacion = (guardado["origen"], guardado["gravedad"], guardado["patron"])
    assert clasificacion == ("manual", "leve", "caida_en_agudos")  # PTA 33,75 dB
    assert guardado["pta_db"] == cuerpo["mean_hearing_loss"]
    assert [p["frequency"] for p in guardado["puntos"]] == [250, 500, 1000, 2000, 4000, 8000]


def test_queda_el_historial_del_mas_nuevo_al_mas_viejo(ana, caso_de_ana):
    primero = _cargar(ana, caso_de_ana).json()["audiograma_id"]
    normal = [{**p, "hearing_loss_db": 10} for p in PUNTOS]
    segundo = _cargar(ana, caso_de_ana, normal).json()["audiograma_id"]
    lista = ana.get(f"/api/casos/{caso_de_ana}/audiogramas").json()
    assert [a["id"] for a in lista] == [segundo, primero]
    assert lista[0]["gravedad"] == "normal"


def test_sin_caso_no_se_guarda(ana, caso_de_ana):
    cuerpo = _cargar(ana).json()
    assert cuerpo["audiograma_id"] is None and cuerpo["patient_name"] == "Nombre a mano"
    assert ana.get(f"/api/casos/{caso_de_ana}/audiogramas").json() == []


def test_desde_archivo_queda_como_archivo(ana, caso_de_ana):
    archivo = "\n".join(f"{p['frequency']},{p['hearing_loss_db']}" for p in PUNTOS)
    respuesta = ana.post("/api/audiogram/upload", files={"file": ("a.csv", archivo, "text/csv")},
                         data={"caso_id": caso_de_ana})
    assert respuesta.status_code == 200
    assert ana.get(f"/api/casos/{caso_de_ana}/audiogramas").json()[0]["origen"] == "archivo"


def test_frecuencias_repetidas_no_se_guardan(ana, caso_de_ana):
    respuesta = _cargar(ana, caso_de_ana, PUNTOS + [{"frequency": 1000, "hearing_loss_db": 30}])
    assert respuesta.status_code == 400
    assert ana.get(f"/api/casos/{caso_de_ana}/audiogramas").json() == []


def test_rn4_el_caso_de_otro_da_404(ana, caso_de_ana, registro_valido):
    beto = _conectado("beto@example.com", registro_valido)
    assert _cargar(beto, caso_de_ana).status_code == 404
    assert beto.get(f"/api/casos/{caso_de_ana}/audiogramas").status_code == 404
    assert ana.get(f"/api/casos/{caso_de_ana}/audiogramas").json() == []


def test_caso_borrado_da_404(ana, caso_de_ana):
    ana.delete(f"/api/casos/{caso_de_ana}")
    assert _cargar(ana, caso_de_ana).status_code == 404
    assert ana.get(f"/api/casos/{caso_de_ana}/audiogramas").status_code == 404
