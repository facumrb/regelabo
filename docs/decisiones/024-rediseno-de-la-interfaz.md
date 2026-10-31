# 024 — Rediseño de la interfaz: paleta turquesa (antes vino), tema claro/oscuro y mobile first

**Fecha:** 2026-10-29 · **Estado:** aceptada

## Contexto
- La interfaz actual es del prototipo: oscura fija, estética "científica" (cuadrícula, glassmorphism) y pensada para PC.
- El usuario es un fonoaudiólogo que no siempre tiene una PC a mano: tiene que poder usarse desde el celular.
- Se armó un prototipo estático (`docs/prototipo-ui/index.html`, datos inventados; `vista.html` muestra móvil y tablet lado a lado) con cinco paletas (A–E) para comparar.

## Decisión
- **Paleta E (vino)**, con tema claro y oscuro. Los colores viven como variables CSS en `frontend/src/index.css` (`--bg`, `--panel`, `--tinta`, `--tenue`, `--linea`, `--acento`, `--acento-tinta`, `--acento-suave`, `--c2`, `--c3`) y Tailwind los expone con los mismos nombres (`bg-panel`, `text-acento`…). Los componentes no usan colores fijos. Todos los pares de texto superan 4,5:1 de contraste en los dos temas.
- **Tema:** atributo `data-tema="claro|oscuro"` en `<html>`. La primera vez sigue al sistema (`prefers-color-scheme`); si el usuario elige uno, se recuerda en `localStorage` (preferencia del navegador, no del usuario en la base). Se aplica antes de pintar con un script en `index.html`, para que no parpadee.
- **Tipografía:** Inter para el texto y JetBrains Mono para valores numéricos.
- **Rutas:** `/` es la pantalla de Inicio (4 bloques) con sesión y la Bienvenida sin sesión; el simulador pasa a `/simular`. La carga de audiograma tiene pantalla propia, sin link en la barra (se llega desde Simular y desde Casos).
- **Navegación:** en PC, barra superior con un menú de usuario desplegable (Cuenta, tema, Salir) en lugar del link "Cuenta"; en el celular, barra inferior de 4 pestañas. Objetivos táctiles de al menos 44 px y tablas que pasan a tarjetas en pantallas chicas.
- **Simular:** todo en una vista (combos de caso y perfil, slider más número editable, vista previa fija).
- No cambia el flujo ni la lógica: es una capa visual sobre las mismas llamadas a la API.
- Se trabaja en la rama `feat/rediseno-ui`, por etapas con un commit cada una: base (colores, tipografía y tema) → navegación → Inicio y Simular → Casos, Historial, Detalle y audiograma → Login, Registro, Cuenta y Bienvenida → documentación.

## Alternativas descartadas
- **Paletas A (grafito + teal), B (crema + violeta), C (grafito + ámbar) y D (salvia + verde bosque):** comparadas en el prototipo; se eligió E.
- **Solo tema oscuro (como ahora):** en consultorio, con luz de día, el claro se lee mejor.
- **Tema fijo la primera vez (claro u oscuro):** seguir al sistema respeta lo que el usuario ya eligió en su dispositivo.
- **Clases `dark:` de Tailwind en cada componente:** duplica cada color; con variables se cambia el tema en un solo lugar.
- **Guardar el tema en la base:** es una preferencia del dispositivo, no hace falta un endpoint.
- **Pantalla de Configuración en el menú:** su contenido no está definido; se suma cuando lo esté.

## Consecuencias
- Durante el rediseño conviven pantallas con el estilo viejo y el nuevo, hasta cerrar la última etapa.
- Los gráficos de Plotly tienen que tomar los colores del tema (hoy tienen colores fijos para el fondo oscuro).
- Cambian las rutas: hay que actualizar los links internos y `docs/guia-de-pruebas.md`.
- Nunca "diagnóstico" en la UI (RN9).

## Ajustes de navegación (2026-10-30)
Tras revisar el rediseño con las pautas de accesibilidad, pensando en alguien que entra por primera vez:
- **Simular es solo para cargar los datos de la simulación:** se sacan las pestañas "Simulación / Carga de Audiogramas" y la línea "Ver historial · Perfil activo" (el historial está en la barra; el perfil, en el selector y en la vista previa).
- **La carga de audiograma tiene ruta propia, `/simular/audiograma`:** funciona el botón atrás y se puede enlazar. Se entra desde el botón "Cargar audiograma" junto al selector de perfil (con una línea de ayuda debajo) y desde la tarjeta y el paso 01 de Inicio. "Volver" retrocede en el historial; "Usar perfil" vuelve a `/simular` con el perfil elegido. Desde Casos todavía no se entra.
- **Pasos de Inicio como enlaces** (01 audiograma, 02 Simular, 03 Historial). El paso 1 de Inicio y Bienvenida pasa a "Cargá un audiograma", porque el caso no tiene audiograma propio.
- **Enlace "Saltar al contenido"** para teclado y lectores de pantalla.
- **El chip del backend y Swagger solo los ven los administradores;** "RAM Stimulus" explica qué es al pasar el mouse.
- **Gráficos de resultados:** las curvas usan una paleta única en orden fijo (`--s1`…`--s6` en `index.css`, validada para daltonismo con la skill `dataviz`) más un tipo de trazo distinto por serie; en la figura 7, el color indica el rol (excitatoria, inhibitoria, neta) y el trazo, el núcleo (CN continuo, IC a guiones). El espectro FFT y el polo de Shera conservan sus colores. La barra de íconos de Plotly se reemplaza por `components/Grafico.tsx`: título en HTML y botones con texto "Restablecer vista" y "Descargar imagen". Las figuras con dos ejes Y se mantienen como en el paper (decisión 023).
- **Simular es solo el paso 1 (cargar datos y esperar):** el resultado ya no aparece debajo del formulario. Mientras espera, el formulario queda desactivado con el estado y un enlace "Seguir en el detalle"; al terminar, el botón dice "✓ Simulación lista" y a los 1,5 s pasa al detalle (`/simulaciones/:id`) con una aparición suave (sin animación si el sistema pide reducir movimiento). Si el resultado se reutiliza (RN10), pasa al instante; si falla, se queda en el formulario con el error. El formulario no queda fijo al bajar y conserva los últimos parámetros.
- **Simular en dos columnas de alto parecido:** a la izquierda el paso 1 (caso, tipo de caso, perfil y la vista previa del audiograma al pie); a la derecha el paso 2 (estímulo, fibras y el botón). Un solo título, "Nueva simulación", con la bajada "Configuración del estímulo acústico y perfil coclear" y el distintivo RAM Stimulus.
- **Detalle con acciones:** "Nueva simulación con estos parámetros", "Nueva simulación", "Ver historial" y "Volver al inicio", también cuando se entra desde el Historial. Arriba vuelve a estar "Volver", que retrocede a la pantalla anterior (o va al historial si el detalle se abrió directo).
- **Simulaciones en curso desde cualquier pantalla:** `context/SimulacionesEnCurso.tsx` consulta su estado; la barra muestra "Simulando… N s", "N simulaciones en curso" o "✓ Resultado listo" (en el celular, un punto sobre Simular) y aparece un aviso discreto de 8 s. Nunca saca a nadie de la pantalla en la que está. Al recargar, se recuperan las en curso entre las últimas 20. Simular sigue esperando una por pestaña; pedir varias seguidas se revisa con la decisión 025.
- Descartados: el audiograma como ítem de la barra (es un paso previo de la simulación y ocuparía una pestaña en el celular) y como opción dentro del selector de perfil (un `<select>` que navega sorprende y es poco accesible).

## Cambio de paleta: turquesa con vino secundario (2026-10-30)

- **Acento turquesa** (`#0f766e` claro / `#2dd4bf` oscuro), el color que se asocia con la fonoaudiología; los fondos y grises pasan de tonos rosados a grises fríos verdosos.
- **Vino como secundario** (`--c2`: `#9f1239` / `#fb7185`): `c2` se dibuja junto al acento (curvas "Pedida" y "Simulada", armónicos de la FFT) y tiene que contrastar con él; el vino además conserva algo de la identidad anterior.
- Siguen superando 4,5:1 todos los pares de texto en los dos temas. Los rojos de error y de borrar no cambian. El punto del estado "ejecutando" pasa a ámbar (`bg-amber-500`): en vino se confundía con el rojo de "error".
- Descartados como secundario: azul índigo (`#4338ca`, más sobrio pero con menos identidad) y ámbar (`#b45309`, se confunde con los avisos).
