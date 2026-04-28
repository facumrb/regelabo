# Información de Directorio: src/utils/

## Propósito exhaustivo
- **`get_RAM_stims.py`**: Herramienta de software que construye matemáticamente una señal acústica o estímulo sonoro de Modulación de Amplitud Rectangular (RAM) dados parámetros como frecuencia de muestreo y portadora.
- **`OHC_ind.py`**: Conjunto de rutinas clínicas encargadas de tomar perfiles reales de audiometría (frecuencias auditivas vs. pérdida en dB) e imputarlos para generar parámetros fisiológicos y perfiles topográficos de "polos", ajustables para casos de simulación patológica.
- **`__init__.py`**: Archivo que marca al directorio `utils/` como un paquete válido de Python.

## Flujo de ejecución
No poseen un ciclo de vida atado secuencialmente al momento principal de cálculo del modelo, sino que operan como herramientas de preprocesamiento. Al preparar una corrida (por ejemplo en `ExampleSimulation.py`), se ejecuta primero una llamada funcional a este directorio (e.g. `get_RAM_stims()`) para obtener matrices previas o perfiles que posteriormente serán introducidos al modelo auditivo central.

## Elemento más relevante
**Archivo `OHC_ind.py`**: Es el componente más destacado porque es la clave de la utilidad clínica del proyecto completo: traduce una lectura audiológica de un paciente al lenguaje matemático necesario para testear daños en el oído virtual.
