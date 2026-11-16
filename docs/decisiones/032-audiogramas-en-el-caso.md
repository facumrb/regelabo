# 032 — Audiogramas guardados en el caso

**Fecha:** 2026-11-16 · **Estado:** aceptada

Resuelve lo que quedaba pendiente de la [019](019-endpoints-del-prototipo-con-sesion.md) y usa las tablas `audiograma` y `punto_audiograma` de la [010](010-esquema-de-datos.md). Es parte del módulo Casos + audiogramas (sección 3 del plan de trabajo, CU2).

## Contexto
- Los perfiles personalizados ya no se pisan ni se ven entre usuarios: desde la 022 la carpeta se nombra con un hash del contenido, y desde la 026 `/profiles` lista solo el catálogo.
- Lo que faltaba era guardar el audiograma: se analizaba, generaba su perfil y se usaba para simular, pero no quedaba en ningún lado. Las tablas existían sin uso.

## Decisión
- **Entrada:** en la pantalla de audiograma, un selector de caso **opcional**; desde la ficha del caso, "Cargar audiograma" la abre con ese caso elegido (`/simular/audiograma?caso=<id>`). Sin caso funciona como antes: genera el perfil y no guarda nada.
- **Con caso:** `POST /api/audiogram/manual` (`caso_id` en el cuerpo) y `/upload` (`caso_id` en el formulario) guardan el audiograma con su origen, PTA, grado y patrón de RN2, el perfil generado y los puntos. El perfil toma el **alias del caso** en lugar de un nombre escrito a mano (decisión 008). Un caso ajeno o borrado da 404 (RN4). Las frecuencias repetidas se rechazan (400, RN1).
- **Historial:** un caso guarda todos sus audiogramas. `GET /api/casos/{id}/audiogramas` los da del más nuevo al más viejo.
- **Ficha del caso:** cada audiograma con grado, patrón, PTA, fecha y origen, la curva (pedida y simulada) y "Simular con este", que abre Simular con el caso y el perfil elegidos.

## Alternativas descartadas
- **Solo desde la ficha del caso:** rompía el camino de Simular → audiograma.
- **Un solo audiograma por caso:** se pierde la evolución de la audición.
- **Mantener el nombre libre con un caso elegido:** invita a escribir el nombre real del paciente.
- **Dejárselo al integrante del módulo:** se hizo antes de la entrega a pedido de Valentino; quedan para ese módulo la validación completa de RN1, borrar audiogramas y el perfil propio con `OHC_ind`.

## Consecuencias
- Sin migración: las tablas ya existían. En la tabla, el patrón con caída en agudos se guarda como `pendiente` (`datos/audiogramas.py` traduce).
- Los endpoints del prototipo reciben el usuario de la sesión y dejan pasar `ErrorDeNegocio` al manejador común.
