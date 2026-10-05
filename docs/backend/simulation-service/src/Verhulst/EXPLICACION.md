# Información de Directorio: Raíz (Verhulstetal2018Model)

## Propósito exhaustivo
- **`src/`**: Contiene todo el código fuente del modelo auditivo computacional (módulos, utilidades, librerías C e interfaces principales).
- **`examples/`**: Contiene los scripts de simulación y análisis escritos en Python para interactuar con el modelo, generar simulaciones RAM y visualizar gráficos.
- **`matlab/`**: Aloja las implementaciones originales y equivalentes del modelo, escritas puramente en MATLAB.
- **`data/`**: Almacena archivos de entrada o recursos fijos, como perfiles precomputados de celdas ciliadas y datos de configuración acústica.
- **`doc/`**: Contiene la documentación técnica, diagramas de bloques e investigaciones en PDF asociadas teóricamente al código.
- **`README.md`, `license.txt`, `.gitignore`**: Archivos de documentación general para el usuario, declaración de licencia legal del código y configuración de repositorios Git.

## Flujo de ejecución
A nivel de la raíz no se ejecuta un flujo directo. El usuario debe ingresar a los scripts ejecutables ubicados en `examples/` o `src/` (como `run_model2018.py`), los cuales accederán a los recursos estáticos de `data/` y correrán la lógica que habita en `src/`.

## Elemento más relevante
**Carpeta `src/`**: Es la más importante debido a que contiene el "motor" del proyecto; sin la lógica matemática y biofísica subyacente alojada ahí, el resto del repositorio carecería de sentido.
