# Información de Directorio: src/core/

## Propósito exhaustivo
- **`cochlear_model2018.py`**: Resuelve las ecuaciones diferenciales del movimiento mecánico y las dinámicas no lineales de la membrana basilar de la cóclea.
- **`inner_hair_cell2018.py`**: Simula el cambio en el potencial de receptor de las células ciliadas internas (IHC) del oído interno al activarse por la velocidad coclear.
- **`auditory_nerve2018.py`**: Transforma los voltajes de las células ciliadas en probabilidades de disparo y picos (spikes) de respuesta neuronal en el nervio auditivo.
- **`ic_cn2018.py`**: Modela las respuestas combinadas originadas en el núcleo coclear (CN) y proyectadas hacia el colículo inferior (IC), simulando métricas profundas como las ondas ABR.
- **`__init__.py`**: Convierte esta carpeta en un paquete nativo de Python para permitir su importación ordenada en otros scripts.

## Flujo de ejecución
El flujo dentro de estos archivos reproduce la trayectoria biológica del sonido en el oído humano. De forma secuencial dentro del tiempo discretizado:
1. Una presión acústica entra al sistema en `cochlear_model2018.py`.
2. Las ondas de velocidad en la membrana son inyectadas a `inner_hair_cell2018.py`.
3. El potencial resultante estimula las fibras del nervio modeladas por `auditory_nerve2018.py`.
4. El conjunto de sinapsis finalmente excita las etapas modeladas en `ic_cn2018.py`.

## Elemento más relevante
**Archivo `cochlear_model2018.py`**: Es el cuello de botella físico y computacional que absorbe el estímulo de entrada originando toda la cascada química y nerviosa del resto de módulos funcionales anatómicos.
