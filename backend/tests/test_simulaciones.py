"""
Simulaciones: parámetros (RN3), cupos (RN5), caché por huella (RN10), aislamiento entre usuarios (RN4)
y el trabajo del worker. El motor se reemplaza por uno falso: el real tarda ~75 s por simulación.
"""

from datetime import datetime, timedelta, timezone

import numpy as np
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from backend.controller import simulaciones
from backend.controller.modelos import ParametrosSimulacion, SimulationResponse
from backend.controller.simulacion import SimulationService
from backend.datos.conexion import engine
from backend.views import crear_app

RESPUESTA_FALSA = SimulationResponse.model_validate({
    "execution_time_seconds": 0.1, "efr_value_uv": 0.2,
    "harmonics": [{"harmonic_order": 1, "frequency_hz": 110.0, "amplitude_uv": 0.1}],
    "fft_spectrum": {"frequencies": [0.0, 110.0], "amplitudes": [0.0, 0.1]},
    "abr_waves": {"time_ms": [0.0, 0.5], "w1": [0.0, 0.1], "w3": [0.0, 0.1], "w5": [0.0, 0.1],
                  "efr_wave": [0.0, 0.3]},
    "parameters_used": {},
    "estados_internos": {
        "canales": [{"frecuencia_solicitada_hz": 1000, "frecuencia_caracteristica_hz": 996.0}],
        "polo_shera": {"fs_hz": 1000, "frecuencia_caracteristica_hz": [996.0], "valores": [[0.06]]},
        "ihc": {"fs_hz": 1e5, "ventana_ms": [0, 50], "canales": [0], "imet_na": [[1.0]], "ikf_na": [[2.0]],
                "iks_na": [[3.0]], "vm_mv": [[-55.0]]},
        "vesiculas": {"fs_hz": 2e4, "ventana_ms": [0, 400],
                      **{f: {"q": [[4.0]], "w": [[14.0]], "a": [[0.9]]} for f in ("hsr", "msr", "lsr")}},
        "cn_ic": {"fs_hz": 2e4, "ventana_ms": [0, 50], "canales": [0], "cn_exc": [[5.0]], "cn_inh": [[1.0]],
                  "ic_exc": [[4.0]], "ic_inh": [[2.0]]},
    },
})


@pytest.fixture
def motor_falso(monkeypatch):
    """Cuenta cuántas veces se ejecutó el modelo."""
    llamadas = []

    def ejecutar(parametros):
        llamadas.append(parametros)
        return RESPUESTA_FALSA

    monkeypatch.setattr(SimulationService, "execute_simulation", staticmethod(ejecutar))
    return llamadas


def _conectado(email, registro_valido, tipo="estudiante"):
    cliente = TestClient(crear_app())
    cliente.post("/api/auth/registro", json={**registro_valido, "email": email, "tipo_perfil": tipo})
    cliente.post("/api/auth/login", json={"email": email, "password": registro_valido["password"]})
    return cliente


@pytest.fixture
def ana(registro_valido):
    return _conectado("ana@example.com", registro_valido)


@pytest.fixture
def beto(registro_valido):
    return _conectado("beto@example.com", registro_valido)


def _pedir(cliente, **cambios):
    return cliente.post("/api/simulaciones", json=cambios)


def _sql(consulta, **parametros):
    with engine.begin() as conexion:
        return conexion.execute(text(consulta), parametros)


def _ejecutando_desde(minutos):
    desde = datetime.now(timezone.utc) - timedelta(minutes=minutos)
    _sql("UPDATE simulacion SET estado = 'ejecutando', iniciada_en = :t", t=desde)


# ---- RN3 ----

@pytest.mark.parametrize("cambio", [
    {"spl_level": -1}, {"spl_level": 101},
    {"carrier_freq": 124}, {"carrier_freq": 8001},
    {"f_mod": 19}, {"f_mod": 1001},
    {"nH": -1}, {"nH": 31}, {"nM": 16}, {"nL": 16},
    {"nH": 0, "nM": 0, "nL": 0},
])
def test_rn3_parametros_fuera_de_rango(ana, motor_falso, cambio):
    respuesta = _pedir(ana, **cambio)
    assert respuesta.status_code == 400
    assert respuesta.json()["detail"]["codigo"] == "parametros_invalidos"


def test_rn3_el_perfil_tiene_que_existir(ana, motor_falso):
    respuesta = _pedir(ana, poles_profile="NoExiste")
    assert respuesta.status_code == 400
    assert respuesta.json()["detail"]["codigo"] == "perfil_inexistente"


def test_rn3_valores_limite_son_validos(ana, motor_falso):
    assert _pedir(ana, spl_level=0, carrier_freq=125, f_mod=1000, nH=0, nM=0, nL=1).status_code == 202


# ---- Pedir, ejecutar y consultar ----

def test_pedir_deja_la_simulacion_en_cola(ana, motor_falso):
    respuesta = _pedir(ana)
    assert respuesta.status_code == 202
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "en_cola" and cuerpo["posicion"] == 1 and cuerpo["resultado"] is None
    assert cuerpo["reutilizada"] is False and "huella" not in cuerpo
    assert motor_falso == []  # pedirla no ejecuta el modelo


def test_el_worker_la_ejecuta_y_queda_completada(ana, motor_falso):
    simulacion_id = _pedir(ana).json()["id"]
    assert simulaciones.procesar_siguiente() is True
    cuerpo = ana.get(f"/api/simulaciones/{simulacion_id}").json()
    assert cuerpo["estado"] == "completada" and cuerpo["posicion"] is None
    assert cuerpo["iniciada_en"] and cuerpo["finalizada_en"]
    assert cuerpo["resultado"]["efr_value_uv"] == 0.2
    assert cuerpo["resultado"]["parameters_used"]["poles_profile"] == "Flat00"
    assert len(motor_falso) == 1


def test_sin_trabajo_el_worker_devuelve_false(motor_falso):
    assert simulaciones.procesar_siguiente() is False


def test_se_toman_en_orden_de_llegada(registro_valido, motor_falso):
    investigadora = _conectado("inv@example.com", registro_valido, "investigador")
    primera = _pedir(investigadora, nH=1).json()["id"]
    segunda = _pedir(investigadora, nH=2).json()
    assert segunda["posicion"] == 2
    simulaciones.procesar_siguiente()
    assert investigadora.get(f"/api/simulaciones/{primera}").json()["estado"] == "completada"
    assert investigadora.get(f"/api/simulaciones/{segunda['id']}").json()["estado"] == "en_cola"


def test_un_error_del_motor_deja_la_simulacion_en_error_y_libera_el_cupo(ana, monkeypatch):
    def falla(parametros):
        raise RuntimeError("detalle interno: /ruta/secreta")

    monkeypatch.setattr(SimulationService, "execute_simulation", staticmethod(falla))
    simulacion_id = _pedir(ana).json()["id"]
    simulaciones.procesar_siguiente()
    cuerpo = ana.get(f"/api/simulaciones/{simulacion_id}").json()
    assert cuerpo["estado"] == "error" and cuerpo["resultado"] is None
    assert "secreta" not in cuerpo["mensaje_error"]  # el detalle interno no llega al usuario
    assert _pedir(ana, nH=5).status_code == 202  # el cupo (1 para estudiantes) quedó libre


def _estados_internos_guardados():
    with engine.connect() as conexion:
        return conexion.execute(text("SELECT datos FROM estados_internos")).scalars().all()


def test_el_worker_guarda_los_estados_internos_aparte(ana, motor_falso):
    simulacion_id = _pedir(ana).json()["id"]
    simulaciones.procesar_siguiente()
    [datos] = _estados_internos_guardados()
    assert datos["ihc"]["imet_na"] == [[1.0]] and datos["canales"][0]["frecuencia_caracteristica_hz"] == 996.0
    # Pesan varios MB: el detalle no los trae (tienen su propio endpoint)
    assert "estados_internos" not in ana.get(f"/api/simulaciones/{simulacion_id}").json()["resultado"]


def test_rn10_un_resultado_reutilizado_no_duplica_los_estados_internos(ana, beto, motor_falso):
    _pedir(ana)
    simulaciones.procesar_siguiente()
    _pedir(beto)
    assert len(_estados_internos_guardados()) == 1


def test_los_estados_internos_se_piden_aparte(ana, motor_falso):
    simulacion_id = _pedir(ana).json()["id"]
    simulaciones.procesar_siguiente()
    respuesta = ana.get(f"/api/simulaciones/{simulacion_id}/estados-internos")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["vesiculas"]["hsr"]["w"] == [[14.0]] and cuerpo["ihc"]["ventana_ms"] == [0, 50]


def test_sin_terminar_no_hay_estados_internos(ana, motor_falso):
    simulacion_id = _pedir(ana).json()["id"]
    respuesta = ana.get(f"/api/simulaciones/{simulacion_id}/estados-internos")
    assert respuesta.status_code == 404
    assert respuesta.json()["detail"]["codigo"] == "estados_internos_no_disponibles"


def test_rn4_los_estados_internos_ajenos_no_existen(ana, beto, motor_falso):
    simulacion_id = _pedir(ana).json()["id"]
    simulaciones.procesar_siguiente()
    respuesta = beto.get(f"/api/simulaciones/{simulacion_id}/estados-internos")
    assert respuesta.status_code == 404
    assert respuesta.json()["detail"]["codigo"] == "simulacion_no_encontrada"


# ---- RN10: caché por huella ----

def test_rn10_un_pedido_identico_reusa_el_resultado(ana, beto, motor_falso):
    _pedir(ana)
    simulaciones.procesar_siguiente()
    reutilizada = _pedir(beto)
    assert reutilizada.status_code == 202
    cuerpo = reutilizada.json()
    assert cuerpo["estado"] == "completada" and cuerpo["reutilizada"] is True
    assert cuerpo["resultado"]["efr_value_uv"] == 0.2
    assert simulaciones.procesar_siguiente() is False and len(motor_falso) == 1


def test_rn10_lo_reutilizado_no_consume_cupo(ana, motor_falso):
    _pedir(ana)  # A
    simulaciones.procesar_siguiente()
    assert _pedir(ana, nH=5).status_code == 202  # B queda en cola: el cupo de estudiante (1) se llena
    assert _pedir(ana, nH=6).status_code == 429
    assert _pedir(ana).json()["reutilizada"] is True  # A otra vez: sale igual


def test_rn10_cualquier_parametro_distinto_cambia_la_huella(ana, motor_falso):
    _pedir(ana)
    simulaciones.procesar_siguiente()
    assert _pedir(ana, spl_level=60).json()["reutilizada"] is False


def test_huella_depende_del_contenido_del_perfil_y_no_solo_del_nombre():
    parametros = ParametrosSimulacion()
    uno, otro = np.zeros(10), np.ones(10)
    huella = simulaciones.calcular_huella
    assert huella(parametros, uno) == huella(parametros, uno.copy())
    assert huella(parametros, uno) != huella(parametros, otro)


# ---- RN5: cupos ----

def test_rn5a_el_estudiante_tiene_un_cupo_simultaneo(ana, motor_falso):
    assert _pedir(ana, nH=1).status_code == 202
    respuesta = _pedir(ana, nH=2)
    assert respuesta.status_code == 429 and respuesta.json()["detail"]["codigo"] == "cupo_agotado"
    simulaciones.procesar_siguiente()  # termina la primera: libera el lugar
    assert _pedir(ana, nH=2).status_code == 202


def test_rn5a_el_investigador_tiene_tres(registro_valido, motor_falso):
    investigadora = _conectado("inv@example.com", registro_valido, "investigador")
    for n in (1, 2, 3):
        assert _pedir(investigadora, nH=n).status_code == 202
    assert _pedir(investigadora, nH=4).json()["detail"]["codigo"] == "cupo_agotado"


def test_rn5a_el_cupo_es_por_usuario(ana, beto, motor_falso):
    assert _pedir(ana, nH=1).status_code == 202
    assert _pedir(beto, nH=2).status_code == 202


def test_rn5b_limite_por_hora(ana, motor_falso):
    for n in range(1, 11):  # el estudiante puede 10 por hora
        assert _pedir(ana, nH=n).status_code == 202
        simulaciones.procesar_siguiente()
    respuesta = _pedir(ana, nH=11)
    assert respuesta.status_code == 429 and respuesta.json()["detail"]["codigo"] == "limite_por_hora"
    assert _pedir(ana, nH=1).json()["reutilizada"] is True  # lo reutilizado no cuenta


def test_rn5b_las_de_hace_mas_de_una_hora_no_cuentan(ana, motor_falso):
    for n in range(1, 11):
        _pedir(ana, nH=n)
        simulaciones.procesar_siguiente()
    _sql("UPDATE simulacion SET creado_en = :t", t=datetime.now(timezone.utc) - timedelta(hours=2))
    assert _pedir(ana, nH=11).status_code == 202


def test_rn5c_el_sistema_se_satura(registro_valido, motor_falso, monkeypatch):
    monkeypatch.setattr(simulaciones, "TOPE_COLA", 2)
    for n in (1, 2):
        assert _pedir(_conectado(f"u{n}@example.com", registro_valido), nH=n).status_code == 202
    respuesta = _pedir(_conectado("u3@example.com", registro_valido), nH=3)
    assert respuesta.status_code == 503 and respuesta.json()["detail"]["codigo"] == "sistema_saturado"


# ---- RN4: aislamiento ----

def test_rn4_una_simulacion_ajena_no_existe(ana, beto, motor_falso):
    simulacion_id = _pedir(ana).json()["id"]
    ajena = beto.get(f"/api/simulaciones/{simulacion_id}")
    inexistente = beto.get("/api/simulaciones/00000000-0000-7000-8000-000000000000")
    assert ajena.status_code == inexistente.status_code == 404 and ajena.json() == inexistente.json()
    assert beto.get("/api/simulaciones").json()["simulaciones"] == []


def test_rn4_no_se_puede_usar_el_caso_de_otro(ana, beto, motor_falso):
    caso_id = ana.post("/api/casos", json={"alias": "De Ana"}).json()["id"]
    respuesta = _pedir(beto, caso_id=caso_id)
    assert respuesta.status_code == 404 and respuesta.json()["detail"]["codigo"] == "caso_no_encontrado"


# ---- Historial ----

def test_el_caso_es_opcional_y_se_puede_filtrar_por_el(registro_valido, motor_falso):
    investigadora = _conectado("inv@example.com", registro_valido, "investigador")
    caso_id = investigadora.post("/api/casos", json={"alias": "Mi caso"}).json()["id"]
    con_caso = _pedir(investigadora, nH=1, caso_id=caso_id).json()
    sin_caso = _pedir(investigadora, nH=2).json()
    assert con_caso["caso_id"] == caso_id and sin_caso["caso_id"] is None
    todas = investigadora.get("/api/simulaciones").json()["simulaciones"]
    assert {s["id"] for s in todas} == {con_caso["id"], sin_caso["id"]}
    filtradas = investigadora.get("/api/simulaciones", params={"caso_id": caso_id}).json()["simulaciones"]
    assert [s["id"] for s in filtradas] == [con_caso["id"]]


def test_el_listado_no_trae_las_senales(ana, motor_falso):
    _pedir(ana)
    simulaciones.procesar_siguiente()
    elemento = ana.get("/api/simulaciones").json()["simulaciones"][0]
    assert elemento["estado"] == "completada" and elemento["resultado"] is None


def test_paginacion_por_cursor_sin_repetir_ni_saltear(registro_valido, motor_falso):
    investigadora = _conectado("inv@example.com", registro_valido, "investigador")
    ids = []
    for n in range(1, 26):
        ids.append(_pedir(investigadora, nH=n).json()["id"])
        simulaciones.procesar_siguiente()
    vistos, cursor, paginas = [], None, 0
    while True:
        params = {"limite": 10} | ({"despues_de": cursor} if cursor else {})
        pagina = investigadora.get("/api/simulaciones", params=params).json()
        vistos += [s["id"] for s in pagina["simulaciones"]]
        paginas += 1
        cursor = pagina["siguiente"]
        if cursor is None:
            break
    assert paginas == 3 and vistos == list(reversed(ids))


@pytest.mark.parametrize("limite", [0, 101])
def test_limite_fuera_de_rango_da_422(ana, limite):
    assert ana.get("/api/simulaciones", params={"limite": limite}).status_code == 422


# ---- Worker caído ----

def test_las_ejecutando_demasiado_tiempo_pasan_a_error(ana, motor_falso):
    vieja = _pedir(ana).json()["id"]
    _ejecutando_desde(minutos=6)
    assert simulaciones.recuperar_interrumpidas() == 1
    cuerpo = ana.get(f"/api/simulaciones/{vieja}").json()
    assert cuerpo["estado"] == "error" and "interrumpió" in cuerpo["mensaje_error"]
    assert _pedir(ana, nH=5).status_code == 202  # y liberó el cupo


def test_las_recientes_no_se_tocan(ana, motor_falso):
    simulacion_id = _pedir(ana).json()["id"]
    _ejecutando_desde(minutos=2)
    assert simulaciones.recuperar_interrumpidas() == 0
    assert ana.get(f"/api/simulaciones/{simulacion_id}").json()["estado"] == "ejecutando"
