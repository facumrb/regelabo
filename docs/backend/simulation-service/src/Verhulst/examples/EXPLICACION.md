# Información de Directorio: examples/

## Propósito exhaustivo
- **`ExampleSimulation.py`**: Archivo de demostración de alto nivel, amigable para el usuario, con la configuración paso a paso, carga de un perfil y un estímulo portador, para testear una simulación del oído, con un post-procesamiento para extraer el EFR e imprimir resultados gráficos.
- **`ExampleAnalysis.py`**: Interfaz de apoyo destinada al usuario final que toma archivos o arreglos provenientes de corridas anteriores y los grafica en dominio de tiempo y frecuencia sin necesidad de re-simular el motor del oído.
- **`ParallelRAMSimulationsEFR.py`**: Un script o *pipeline* robusto destinado a la experimentación científica que usa librerías de multiprocesamiento para simular y calcular métricas EFR sobre listados o lotes enteros (batches) de pacientes a partir de perfiles de Excel.

## Flujo de ejecución
El usuario debe lanzar comandos directos hacia este directorio (e.g. `python ExampleSimulation.py`).
El flujo típico implica invocar herramientas y funciones alojadas en `src/`: 
1. Obtener y construir la onda estímulo requerida.
2. Leer y cargar perfiles `.dat` fisiológicos.
3. Iniciar el motor en `model2018` desde la importación `src.model2018`.
4. Evaluar los potenciales neuronales o aplicar transformadas matemáticas finales.
5. Exportar CSV, archivos `.mat` de guardado y gráficos resultantes (`matplotlib`).

## Elemento más relevante
**Archivo `ExampleSimulation.py`**: Representa el modelo operativo "Ideal" de esta herramienta científica, demostrando con código fácil de seguir la metodología completa requerida para poner en práctica las demás librerías en cascada.
