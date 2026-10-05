# Información de Directorio: data/

## Propósito exhaustivo
- **`Poles/`**: Subdirectorio central que actúa como una gran base de datos jerárquica con docenas de variantes patológicas de perfiles topográficos pre-computados para las células del modelo.
- **`StartingPoles.dat`**: Un archivo independiente de perfil genérico predeterminado en la raíz de los datos. Contiene los coeficientes de un sistema biológico sano (o plano) para poder arrancar simulaciones predeterminadas rápidamente sin configurar un paciente complejo.

## Flujo de ejecución
No tienen flujo de ejecución ni procesos algorítmicos. Son ficheros estáticos con configuraciones matemáticas u objetivos analíticos. Cuando un usuario corre `ExampleSimulation.py` u otra orquestación, se referencian estáticamente los caminos, se abren en modo de lectura y se instalan en las variables que darán ignición a la función de la cóclea.

## Elemento más relevante
**Carpeta `Poles/`**: Consiste en la espina dorsal fisiológica precomputada que permite someter a la cóclea a condiciones de oídos reales y patológicos. Sin el repositorio estructurado de este directorio, todas las respuestas obtenidas del código serían simplemente mecánicas, planas e irreales.
