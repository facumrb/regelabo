"""
Proceso que ejecuta las simulaciones en cola (decisión 005). Corre aparte de la API:

    uv run python worker.py

Ejecuta una simulación a la vez (~1,1 GB de RAM y un núcleo cada una). Para atender más en paralelo
se levantan más procesos. No se recarga solo: hay que reiniciarlo si cambia el código.
"""

import logging
import time

from backend.controller import simulaciones

PAUSA_SIN_TRABAJO_S = 2

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("worker")


def main() -> None:
    logger.info("Worker iniciado. Esperando simulaciones…")
    while True:
        interrumpidas = simulaciones.recuperar_interrumpidas()
        if interrumpidas:
            logger.warning("%d simulación(es) interrumpida(s) marcadas con error", interrumpidas)
        if simulaciones.procesar_siguiente():
            logger.info("Simulación procesada")
        else:
            time.sleep(PAUSA_SIN_TRABAJO_S)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Worker detenido")
