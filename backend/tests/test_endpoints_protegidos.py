"""Los endpoints de simulación y audiogramas piden sesión; /health sigue público."""

import pytest

PUNTOS = [{"frequency": 500, "hearing_loss_db": 20}, {"frequency": 4000, "hearing_loss_db": 40}]


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
    ("post", "/api/simulaciones", {}),
    ("get", "/api/simulaciones", None),
    ("get", "/api/simulaciones/00000000-0000-7000-8000-000000000000", None),
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
    assert respuesta.status_code == 200 and "Flat00" in [p["nombre"] for p in respuesta.json()]


@pytest.mark.parametrize("perfil", ["../secreto", "Flat00/../../x", "con espacio", "a" * 101, ""])
def test_nombre_de_perfil_invalido_da_422(ana, perfil):
    assert ana.post("/api/simulaciones", json={"poles_profile": perfil}).status_code == 422
