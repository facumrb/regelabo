# Información de Directorio: matlab/

## Propósito exhaustivo
- **`model2018.m`**: Archivo fuente del motor general del modelo auditivo pero transcrito explícitamente en lenguaje MATLAB, conteniendo todos los lazos, llamadas físicas y resolución de ecuaciones nativas.
- **`ExampleAnalysis.m`**: Archivo equivalente al graficador en Python; sirve en este entorno para realizar el dibujo de las oscilaciones neuronales.
- **`ExampleSimulation.m`**: Orquestador y punto de partida para ejecutar los scripts de MATLAB, configurando datos fisiológicos, variables y enviando matrices hacia la lógica de `model2018.m`.

## Flujo de ejecución
Estos archivos son exclusivos para los usuarios que prefieren (o solo tienen) el entorno de software propietario de The MathWorks (MATLAB). Al ejecutar en consola `ExampleSimulation`, las funciones declaran las variables estáticas y realizan el llamado de arreglos numéricos (como en un diagrama de bloques tradicional de Simulink/MATLAB) hacia `model2018.m`, produciendo respuestas auditivas biológicas.

## Elemento más relevante
**Archivo `model2018.m`**: Al tratarse de la programación original que se liberó junto a las conclusiones biológicas del equipo científico de 2018, es el documento de control definitivo. Cualquier adaptación en Python debe alinearse metodológica y numéricamente a este archivo.
