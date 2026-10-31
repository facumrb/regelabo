# 026 — Etiquetas clínicas y catálogo de perfiles

**Fecha:** 2026-10-30 · **Estado:** aceptada (terminología provisoria hasta la revisión de fonoaudiología)

Completa la [022](022-perfiles-auditivos.md).

## Contexto
- Los perfiles precargados usan la abreviatura de Verhulst (`Flat30`, `Slope20_5`, `Flat30_Slope35`). Las etiquetas de la 022 describían la curva en términos técnicos ("Descendente desde 1 kHz · 20 dB HL a 8 kHz, graves en 5 dB HL · normal (PTA 8.7)"), sin decir qué tipo de caso es.
- Los 13 perfiles descendentes dan PTA "normal" (RN2 promedia 500 Hz–4 kHz y la caída está sobre todo en 8 kHz): la etiqueta decía solo "normal".
- RN2 llamaba al patrón "pendiente" y la interfaz, "descendente".
- El catálogo tenía 22 perfiles, varios casi iguales (`Slope10_5`, PTA 6.2, y `Slope25`, PTA 6.1). En Inicio, el historial y el detalle se veía el nombre crudo del modelo.

## Decisión
- **Etiqueta = nombre clínico + detalle de la curva**, con el grado de RN2 y la configuración, en el vocabulario de un informe audiométrico: "Audición normal · plana en 15 dB HL", "Hipoacusia leve plana · 25 dB HL", "Normal con caída en agudos · hasta 35 dB HL en 8 kHz", "Hipoacusia leve plana con caída en agudos · 30 dB HL, hasta 35 en 8 kHz". El PTA se muestra aparte (vista previa y detalle). Los personalizados siguen siendo "<nombre> (personalizado)".
- **"Caída en agudos (descendente)"** reemplaza a "pendiente" en RN2 y en la interfaz.
- **Catálogo de 9 perfiles** (`CATALOGO` en `controller/perfiles.py`): `Flat00`, `Flat15`, `Flat25`, `Flat35`, `Slope15`, `Slope25`, `Slope35`, `Slope35_5` y `Flat30_Slope35`. Van del caso normal al techo del modelo (35 dB HL) en pasos de ~10 dB. `GET /profiles` devuelve solo esos; `GET /profiles/{nombre}` y las simulaciones aceptan cualquiera, así que las simulaciones viejas siguen funcionando. No se borran carpetas ni se toca la base: los 8 planos son la tabla de la que salen los perfiles nuevos.
- Las demás configuraciones se recrean desde "Cargar audiograma" (la 022 las reconstruye con 0,18 dB de error medio). El selector lo dice: "¿Buscás otra configuración? Cargá su audiograma y se genera el perfil."
- **Dos selectores en Simular: "Tipo de caso" y "Perfil auditivo".** Los tipos son Audición normal (plana con grado normal de RN2: `Flat00`, `Flat15`), Hipoacusia plana (`Flat25`, `Flat35`), Caída en agudos (los 4 `Slope`) y Plana + caída en agudos (`Flat30_Slope35`), más "Desde tu audiograma" cuando hay un perfil personalizado. El segundo muestra solo lo que cambia dentro del tipo ("Hasta 25 dB HL en 8 kHz") y se ve aunque haya una sola opción. Al cambiar de tipo se elige su perfil de menor pérdida. El tipo se calcula en el frontend con `forma` y `grado`, sin cambiar la API.
- **Perfiles desde un audiograma:** en el historial y el detalle se clasifican con RN2 como los precargados y se marca su origen ("Caída en agudos (tu audiograma)"), con el nombre que les puso el usuario y su PTA ("Mi perfil · PTA 28 dB HL"). El patrón de RN2 viaja en `PerfilAuditivo.patron` (`perfiles.patron()`, que también usa la carga de audiograma). En el selector de Simular siguen bajo "Desde tu audiograma".
- **La etiqueta reemplaza al nombre del modelo** en Inicio, el historial y el detalle; el historial lo separa en dos columnas, "Tipo de caso" y "Perfil auditivo" (`components/perfiles.ts` comparte la lógica con el selector); el detalle muestra además "Perfil del modelo: `Slope20_5`" para quien quiera replicar la simulación.

## Alternativas descartadas
- **Sumar una referencia de causa** ("patrón similar a una presbiacusia incipiente"): ayuda a los estudiantes, pero sugiere una causa (roza RN9) y necesita la validación de fonoaudiología. El trauma acústico (caída en 4 kHz) tampoco se puede representar con estos perfiles. Se reconsidera después de esa revisión.
- **Solo reordenar la etiqueta actual** ("Leve · plana 30 dB HL"): sigue sin nombrar el tipo de caso.
- **Dejar los 22 perfiles:** las variantes de 5 dB se distinguen solo por un número y alargan el selector sin aportar casos distintos.
- **Borrar las carpetas ocultas:** rompería las simulaciones viejas que las usan.

## Consecuencias
- Una variante recreada desde el audiograma tiene otra huella: no reutiliza el resultado viejo y vuelve a correr.
- La terminología entra en la revisión pendiente de fonoaudiología, junto con el panel de estados internos (decisión 023).
- Cambiar el recorte del catálogo es editar `CATALOGO`.
