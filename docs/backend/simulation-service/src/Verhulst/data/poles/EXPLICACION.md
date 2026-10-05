# Información de Directorio: data/Poles/

## Propósito exhaustivo
- **Carpetas internas (`Flat00`, `Slope05`, `Normal`, `Flat35`, etc.)**: Corresponden a incontables casos y subcategorías de audiometría o pérdidas tonales clínicas de pacientes. "Slope" representa pérdida en pendiente hacia frecuencias agudas, mientras que "Flat" encaja en un daño en bloque de todo el ancho espectral. Adentro guardan matrices `.dat`.

## Flujo de ejecución
Estos recursos carecen de flujo de ejecución. Se consultan dinámicamente durante el tiempo de inicialización de las simulaciones en Python a través de utilidades en base a cadenas formateadas como `poles_path = '../data/Poles/{poles_profile}/StartingPoles.dat'`, entregando un panorama biomecánico personalizado según el tipo de daño del paciente a analizar.

## Elemento más relevante
**Cualquier subcarpeta representativa (como `Normal/` o `Flat00/`)**: Son el alma de la experimentación computacional. La simple inserción de uno de estos conjuntos a las variables en lugar del perfil biológico `Normal` someterá virtualmente al paciente algorítmico a sordera temporal, disfunciones sinápticas o patologías acústicas complejas.
