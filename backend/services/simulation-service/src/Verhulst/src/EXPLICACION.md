# Información de Directorio: src/

## Propósito exhaustivo
- **`core/`**: Subcarpeta fundamental que agrupa los módulos fisiológicos y anatómicos del sistema auditivo (membrana de cóclea, células ciliadas, nervio, etc.).
- **`utils/`**: Subcarpeta de herramientas y utilidades complementarias para generar estímulos (señales RAM) y procesar entradas como audiogramas.
- **`c_lib/`**: Subcarpeta de bajo nivel con implementaciones en C y scripts de compilación para cálculos de alto rendimiento y resolución de matrices tridiagonales.
- **`model2018.py`**: Función central integradora de Python que importa todos los módulos anatómicos, inicializa la simulación para canales paralelos y entrega una estructura con los resultados consolidados.
- **`run_model2018.py`**: Interfaz/Script original que lee configuraciones desde archivos `.mat` y coordina una corrida paralela utilizando los módulos principales.

## Flujo de ejecución
El script `model2018.py` funciona como el nodo central del flujo en esta carpeta. Un llamado a esta función instanciará objetos de `core.cochlear_model2018` para calcular la cóclea, cuyos resultados en cascada estimularán a `core.inner_hair_cell2018`, luego pasarán a `core.auditory_nerve2018` y terminarán en los núcleos auditivos del tronco encefálico alojados en `core.ic_cn2018`. A su vez, para los cálculos matemáticos, `core` invoca los componentes compilados que nacen de `c_lib`.

## Elemento más relevante
**Archivo `model2018.py`**: Actúa como el puente interactivo del modelo completo. Es la clase/función maestra que oculta la complejidad anatómica de las demás piezas biológicas, orquestándolas y devolviéndolas empacadas al usuario.
