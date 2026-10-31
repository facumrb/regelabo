# 022 — Perfiles auditivos: forma real del audiograma y techo del modelo

**Fecha:** 2026-10-17 · **Estado:** aceptada

## Contexto
- El modelo no recibe audiogramas sino polos (`StartingPoles.dat`). El repo trae 33 perfiles precalculados, con nombres crípticos (`Flat00_Slope15`, `Slope20_5`) y 11 duplicados (`Normal` ≈ `Flat00`, cuyo `profile.txt` además no corresponde a sus polos).
- Un audiograma se convertía **copiando el perfil precalculado más cercano**, así que se perdía la forma de la curva (por ejemplo, la caída en 4 kHz del trauma acústico).
- **El modelo tiene un techo que depende de la frecuencia.** Solo representa la pérdida de las células ciliadas externas: el polo se satura en el daño máximo (0,302) a ~20 dB HL en 250 Hz, 25 en 500 Hz, 30 en 1–2 kHz y 35 en 4–8 kHz. `OHC_ind` también recorta en silencio (`OHC_ind.py:276`). La pantalla mostraba "moderada" y simulaba una pérdida menor, sin avisar.

## Decisión
- **Perfiles propios por aproximación:** los polos de un audiograma salen de la tabla "dB HL → polo" de los 8 perfiles planos (`Flat00`…`Flat35`), sección por sección. Es la misma búsqueda que hace `OHC_ind`, pero con una tabla más gruesa (pasos de 5 dB), y no necesita los `.mat` bloqueados por la licencia. **Validación:** reconstruye los 24 perfiles no planos con un error medio de 0,18 dB y un máximo de 4,7 dB, menos de un paso de audiometría (`tests/test_perfiles.py`).
- **Transparencia:** cada perfil trae la curva pedida y la simulada (la pedida recortada al techo). Si alguna frecuencia se recorta más de 5 dB, hay un **cartel fijo antes de simular** y un **aviso final** con las dos curvas, en el resultado y en el detalle del historial.
- **Catálogo para el profesional** (las etiquetas y el recorte a 9 perfiles cambiaron en la [026](026-etiquetas-clinicas-de-los-perfiles.md)): `GET /profiles` devuelve los 22 perfiles base, sin duplicados, con su etiqueta ("Descendente desde 1 kHz · 35 dB HL a 8 kHz · normal (PTA 8.5)"), el grado según RN2 y las curvas. Todo el filtrado lo hace el backend. `GET /profiles/{nombre}` devuelve uno, también si es personalizado.
- **Personalizados:** la carpeta es `Custom_<hash del nombre y la curva>` (nunca se pisa y el mismo audiograma la reusa), y el nombre visible es "<nombre del usuario> (personalizado)", guardado en `perfil.json`. No se listan en `/profiles`. El campo pasa a llamarse "Nombre del perfil" y pide no usar nombres reales (decisión 008).
- Las etiquetas se calculan leyendo `profile.txt` una sola vez, sin tabla en la base.

## Alternativas descartadas
- **Seguir copiando el perfil más cercano (corrigiendo la distancia):** es honesto si se muestran las dos curvas, pero simula otra forma de curva.
- **Bloquear los audiogramas que superan el techo:** deja afuera los casos moderados y severos.
- **Esperar a `OHC_ind`:** está bloqueado por la licencia y tendría el mismo techo.
- **Ventana de confirmación antes de simular:** se cierra sin leer. Se prefirió un cartel fijo.
- **Renombrar las carpetas de Verhulst:** toca el código del modelo y la huella de lo ya simulado.
- **Tabla `perfil` en la base:** requiere migración y sincronizarla con las carpetas. Tiene sentido cuando los perfiles se liguen a un Caso.

## Consecuencias
- **Para el módulo de audiogramas (Compañero A):** reemplazar la tabla por `OHC_ind` cuando estén los `.mat`, medir el techo real con `SMax`, ligar los personalizados a un Caso (RN4) y validar RN1.
- El techo se estima en pasos de 5 dB (primer nivel saturado): el real puede estar hasta 5 dB más abajo.
- Las carpetas `Custom_*` anteriores siguen simulando, pero `GET /profiles/{nombre}` da 404 porque no guardaron el audiograma.
