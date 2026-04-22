# Información de Directorio: src/c_lib/

## Propósito exhaustivo
- **`cochlea_utils.c`**: Código de muy bajo nivel escrito en lenguaje C para aprovechar punteros y estructuras de matrices de alta velocidad. Contiene el solucionador estricto para ecuaciones y matrices tridiagonales (fundamentales en modelos de fluidos de la cóclea).
- **`build.bat`**: Archivo Batch o macro para sistemas operativos Windows, destinado a invocar al compilador `gcc` y transformar el código C en un binario local (`tridiag.dll`).
- **`build.sh`**: Equivalente del shell script para sistemas Linux/macOS, utilizado para generar bibliotecas de tipo `.so`.
- **`__init__.py`**: Define la presencia de Python para referenciar este paquete (aunque aloje código en C/Bash).

## Flujo de ejecución
El flujo es de construcción única en todo el repositorio. Como pre-requisito, un usuario debe ejecutar `build.bat` (o `build.sh`) que genera la librería dinámica compartida (`.dll`/`.so`). Una vez compilado, durante toda simulación futura el módulo en Python de la cóclea enlazará interactivamente esta librería por debajo (vía punteros `ctypes`), evadiendo ejecutar ciclos costosos desde el propio script en Python.

## Elemento más relevante
**Archivo `cochlea_utils.c`**: Aloja toda la complejidad del optimizador que permite que el modelo Verhulstetal2018 pueda ser simulado de manera realista y manejable de lado del procesamiento por el CPU de la PC sin que tome una cantidad de tiempo prohibitiva.
