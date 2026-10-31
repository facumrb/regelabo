"""
Perfiles auditivos (decisión 022): la tabla de los planos reproduce los demás perfiles, el techo recorta
y avisa, el catálogo no repite perfiles y los personalizados no se pisan.
"""

import numpy as np
import pytest

from backend.controller import perfiles
from backend.controller.modelos import AudiogramPoint
from backend.datos import perfiles as datos_perfiles

TRAUMA = [(250, 10), (500, 15), (1000, 15), (2000, 25), (4000, 60), (8000, 30)]


def _puntos(pares):
    return [AudiogramPoint(frequency=f, hearing_loss_db=db) for f, db in pares]


def _a_db(polos, polos_planos, techo):
    """Pasa cada polo a dB HL con la tabla, salvo en la zona saturada (ahí cualquier dB da el mismo polo)."""
    niveles = np.array(perfiles.NIVELES_PLANOS, dtype=float)
    db = np.full(len(polos), np.nan)
    for k, polo in enumerate(polos):
        hasta = int(np.searchsorted(niveles, techo[k])) + 1
        db[k] = np.interp(polo, polos_planos[:hasta, k], niveles[:hasta])
    return db


@pytest.mark.parametrize("nombre", ["Slope20", "Slope35", "Slope20_5", "Slope35_5", "Flat30_Slope35"])
def test_la_tabla_de_los_planos_reconstruye_los_demas_perfiles(nombre):
    frecuencias, polos_planos, techo = perfiles._tabla()
    curva = datos_perfiles.cargar_curva(nombre)
    # model_construct: la curva cubre hasta ~20 kHz, más allá del rango que se acepta de un usuario
    puntos = [AudiogramPoint.model_construct(frequency=f, hearing_loss_db=db) for f, db in zip(*curva)]
    generados = perfiles.generar_polos(puntos)
    originales = datos_perfiles.cargar_polos(nombre)

    assert generados[0] == generados[1]  # el oído medio repite la primera sección
    pedido = curva[1]
    fuera_del_techo = pedido < techo
    error = np.abs(_a_db(generados[1:], polos_planos, techo) - _a_db(originales[1:], polos_planos, techo))
    # el promedio de todos los perfiles es 0,18 dB; el peor por perfil, 1,23 dB (Flat30_Slope35)
    assert error[fuera_del_techo].mean() < 1.5
    assert error[fuera_del_techo].max() < 5  # menos de un paso de audiometría


def test_el_techo_sube_con_la_frecuencia():
    techo = [perfiles._tabla()[2][perfiles._seccion(f)] for f in (250, 1000, 8000)]
    assert techo == sorted(techo) and techo[0] < techo[-1] == 35


def test_lo_que_supera_el_techo_se_recorta_y_se_avisa():
    perfil = perfiles._armar("x", "personalizada", "x", _puntos(TRAUMA))
    simulada = {p.frequency: p.hearing_loss_db for p in perfil.curva_simulada}
    assert simulada[4000] < 60 and simulada[1000] == 15  # la caída en 4 kHz queda, recortada
    assert perfil.frecuencias_recortadas == [4000]


def test_un_recorte_de_hasta_5_db_no_avisa():
    techo_250 = perfiles._tabla()[2][perfiles._seccion(250)]
    perfil = perfiles._armar("x", "personalizada", "x", _puntos([(250, techo_250 + 5), (4000, 0)]))
    assert perfil.frecuencias_recortadas == []


def test_el_catalogo_tiene_solo_los_9_perfiles_elegidos():
    lista = perfiles.listar()
    nombres = [p.nombre for p in lista]
    assert set(nombres) == perfiles.CATALOGO
    assert not any(n.startswith(perfiles.PREFIJO_PERSONALIZADO) for n in nombres)
    curvas = [tuple(p.hearing_loss_db for p in perfil.curva_pedida) for perfil in lista]
    assert len(curvas) == len(set(curvas))


def test_etiquetas_clinicas_con_el_grado_de_rn2():
    por_nombre = {p.nombre: p for p in perfiles.listar()}
    assert por_nombre["Flat00"].etiqueta.startswith("Audición normal")
    assert por_nombre["Flat15"].etiqueta == "Audición normal · plana en 15 dB HL"
    assert por_nombre["Flat25"].etiqueta == "Hipoacusia leve plana · 25 dB HL"
    descendente = por_nombre["Slope35_5"]
    assert descendente.forma == "descendente"
    assert descendente.etiqueta == "Normal con caída en agudos · de 5 dB HL en graves a 35 dB HL en 8 kHz"
    assert por_nombre["Flat30_Slope35"].etiqueta.startswith("Hipoacusia leve plana con caída en agudos")


def test_un_perfil_fuera_del_catalogo_sigue_disponible_con_su_etiqueta():
    perfil = perfiles.ver("Slope20_5")  # lo usan simulaciones viejas
    assert perfil.etiqueta == "Normal con caída en agudos · de 5 dB HL en graves a 20 dB HL en 8 kHz"


@pytest.fixture
def carpeta_temporal(tmp_path, monkeypatch):
    perfiles._tabla()  # la tabla sale de los perfiles reales; después se escribe en una carpeta aparte
    monkeypatch.setattr(datos_perfiles, "POLES_DIR", str(tmp_path))
    return tmp_path


def test_el_personalizado_lleva_el_nombre_del_usuario_y_no_se_pisa(carpeta_temporal):
    primero = perfiles.crear_personalizado("Trauma caso 12", _puntos(TRAUMA))
    otra_curva = perfiles.crear_personalizado("Trauma caso 12", _puntos(TRAUMA[:-1] + [(8000, 40)]))
    de_nuevo = perfiles.crear_personalizado("Trauma caso 12", _puntos(TRAUMA))

    assert primero.etiqueta.startswith("Trauma caso 12 (personalizado)")
    assert "Trauma" not in primero.nombre  # la carpeta no lleva lo que escribió el usuario
    assert otra_curva.nombre != primero.nombre and de_nuevo.nombre == primero.nombre
    assert perfiles.ver(primero.nombre).curva_pedida == primero.curva_pedida


def test_un_perfil_que_no_existe_da_404(cliente, registro_valido):
    cliente.post("/api/auth/registro", json=registro_valido)
    cliente.post("/api/auth/login", json={"email": registro_valido["email"],
                                          "password": registro_valido["password"]})
    assert cliente.get("/api/profiles/Flat20").json()["nombre"] == "Flat20"
    respuesta = cliente.get("/api/profiles/NoExiste")
    assert respuesta.status_code == 404 and respuesta.json()["detail"]["codigo"] == "perfil_no_encontrado"


def test_el_personalizado_se_clasifica_con_rn2(carpeta_temporal):
    perfil = perfiles.crear_personalizado("Caída", _puntos([(250, 10), (1000, 10), (4000, 40), (8000, 50)]))
    assert perfil.patron == "caida_en_agudos" and perfil.grado == "normal"  # PTA 17,5: normal
    plano = perfiles.crear_personalizado("Plano", _puntos([(250, 30), (1000, 30), (4000, 35), (8000, 35)]))
    assert plano.patron == "plano" and plano.grado == "leve"
