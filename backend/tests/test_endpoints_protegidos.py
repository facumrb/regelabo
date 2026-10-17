"""Los endpoints de simulación y audiogramas piden sesión; /health sigue público."""

import pytest

from backend.controller.modelos import SimulationResponse
from backend.controller.simulacion import SimulationService

PUNTOS = [{"frequency": 500, "hearing_loss_db": 20}, {"frequency": 4000, "hearing_loss_db": 40}]
RESPUESTA_FALSA = SimulationResponse.model_validate({
    "execution_time_seconds": 0.1, "efr_value_uv": 0.2, "harmonics": [],
    "fft_spectrum": {"frequencies": [], "amplitudes": []},
    "abr_waves": {"time_ms": [], "w1": [], "w3": [], "w5": [], "efr_wave": []},
    "parameters_used": {},
})


@pytest.fixture
def ana(cliente, registro_valido):
    cliente.post("/api/auth/registro", json=registro_valido)
    cliente.post("/api/auth/login", json={"email": registro_valido["email"],
                                          "password": registro_valido["password"]})
    return cliente


def test_health_es_publico(cliente):
    assert cliente.get("/api/health").status_code == 200


@pytest.mark.parametrize("metodo, ruta, cuerpo", [
    ("get", "/api/profiles", None),
    ("post", "/api/simulate", {}),
    ("post", "/api/audiogram/manual", {"points": PUNTOS}),
])
def test_sin_sesion_da_401(cliente, metodo, ruta, cuerpo):
    respuesta = getattr(cliente, metodo)(ruta, **({"json": cuerpo} if cuerpo is not None else {}))
    assert respuesta.status_code == 401
    assert respuesta.json()["detail"]["codigo"] == "no_autenticado"


def test_subir_audiograma_sin_sesion_da_401(cliente):
    respuesta = cliente.post("/api/audiogram/upload", files={"file": ("a.csv", b"500,20\n4000,40")})
    assert respuesta.status_code == 401


def test_con_sesion_los_perfiles_se_listan(ana):
    respuesta = ana.get("/api/profiles")
    assert respuesta.status_code == 200 and "Flat00" in respuesta.json()


def test_con_sesion_simula(ana, monkeypatch):
    monkeypatch.setattr(SimulationService, "execute_simulation", staticmethod(lambda req: RESPUESTA_FALSA))
    respuesta = ana.post("/api/simulate", json={"poles_profile": "Flat00"})
    assert respuesta.status_code == 200 and respuesta.json()["efr_value_uv"] == 0.2


@pytest.mark.parametrize("perfil", ["../secreto", "Flat00/../../x", "con espacio", "a" * 101, ""])
def test_nombre_de_perfil_invalido_da_422(ana, perfil):
    assert ana.post("/api/simulate", json={"poles_profile": perfil}).status_code == 422
