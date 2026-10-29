"""Equivalencia numérica de los estados internos (decisión 023).

Guardar los estados internos no debe alterar el compuesto EFR/ABR: se compara contra una corrida del
modelo sin `d`. Corre el modelo dos veces (~3 min); usar `uv run pytest -m lento` con tope de memoria.
"""

import os
import tempfile

import numpy as np
import pytest

from backend.services import motor

pytestmark = pytest.mark.lento

POLOS = np.loadtxt(os.path.join(motor.VERHULST_SRC, "..", "data", "Poles", "Flat00", "StartingPoles.dat"))
PARAMETROS = dict(frecuencia_portadora=4000.0, nivel_db_spl=70.0, frecuencia_modulacion=110.0,
                  n_h=13, n_m=3, n_l=3)


def _ondas_sin_estados_internos():
    estimulo = motor.get_RAM_stims(fs=motor.FS_ESTIMULO, fRAM=np.array([4000.0]), level=70.0,
                                   fMod=110.0, dur=motor.DURACION_ESTIMULO_S)
    carpeta_original = os.getcwd()
    with tempfile.TemporaryDirectory() as carpeta:
        os.chdir(carpeta)
        try:
            salida = motor.model2018(estimulo, motor.FS_ESTIMULO, fc='abr', irregularities=1, storeflag='bw',
                                     subject=motor.SEMILLA, sheraPo=POLOS, IrrPct=0.05, non_linear_type='vel',
                                     nH=13, nM=3, nL=3, clean=1, data_folder='./', graficar=False)[0]
        finally:
            os.chdir(carpeta_original)
    return salida


@pytest.fixture(scope="module")
def con_estados_internos():
    return motor.ejecutar_modelo(POLOS, **PARAMETROS)


def test_las_ondas_no_cambian_al_guardar_estados_internos(con_estados_internos):
    sin = _ondas_sin_estados_internos()
    for onda in ("w1", "w3", "w5"):
        np.testing.assert_array_equal(getattr(con_estados_internos, onda), getattr(sin, onda).flatten())


def test_los_estados_internos_informan_canal_y_tienen_la_forma_esperada(con_estados_internos):
    estados = con_estados_internos.estados_internos
    for canal in estados["canales"]:
        pedida, efectiva = canal["frecuencia_solicitada_hz"], canal["frecuencia_caracteristica_hz"]
        assert abs(efectiva - pedida) / pedida < 0.05
    assert estados["polo_shera"]["valores"].shape == (400, 401)
    assert estados["ihc"]["imet_na"].shape == (5000, 2)
    assert estados["cn_ic"]["cn_exc"].shape == (1000, 2)
    assert estados["vesiculas"]["hsr"]["q"].shape == (8000, 4)
