# 034 — Vista para celular y tablet

**Fecha:** 2026-11-17 · **Estado:** aceptada

Ajusta el diseño mobile first de la [024](024-rediseno-de-la-interfaz.md). Las opciones se evaluaron con el prototipo `prototipo-mobile.html` (raíz del repo), que muestra el antes y el después en 390 px y 820 px.

## Contexto
- Tablet vertical (768–1023 px): las secciones pasaban a la barra superior (`md:`) junto con el indicador, el estado del servidor y el nombre, y no entraban.
- Historial: 8 columnas en la tablet y una tarjeta de ~280 px por simulación en el celular.
- Resultado: 5 acciones sueltas, 10 parámetros desordenados y gráficos de 384 px con la leyenda sobre el eje X; arrastrar para ampliar no dejaba hacer scroll con el dedo.
- Simular: en el celular, el botón quedaba a ~2 pantallas de distancia; en la tablet, una sola columna muy estirada.
- Superponer: en el celular, la tabla de diferencias obligaba a desplazar de costado.

## Decisión
- **Navegación (opción A):** barra inferior de pestañas hasta `lg` (1024 px). Se movieron a `lg:` los desplazamientos que dependen de ella (`App.tsx`, `PanelPruebas`, aviso de simulación terminada, barra de Superponer del Historial).
- **Pie:** en el celular, una línea ("Basado en Verhulst et al. (2018)").
- **Simular:** dos columnas desde `md`; en el celular, barra fija sobre las pestañas con el perfil, el estímulo y el botón "Simular".
- **Resultado:** acción principal + "Superponer con…" (desde la tablet) + menú ⋯ (`MasAcciones` en `ui.tsx`: hoja desde abajo en el celular, desplegable en la tablet); en PC siguen todas a la vista. Parámetros plegados en el celular y en grilla desde la tablet. Tarjetas del EFR en 2 columnas hasta `lg`.
- **Gráficos (opción A):** alto 240 / 320 / 384 px, leyenda arriba, y en pantallas táctiles sin arrastre para ampliar y con "Pantalla completa" (gira a horizontal donde el navegador lo permite).
- **Historial (opción B):** lista propia (no el componente `Tabla`, que sigue en Mis casos): fila compacta con la casilla a la izquierda en el celular y tabla de 6 columnas desde la tablet.
- **Superponer (opción A):** en el celular, un bloque por dato; si el valor es igual en todas, una línea. Guardar + menú ⋯ (Borrar, CSV, Imprimir).

## Alternativas descartadas
- **Secciones solo con íconos arriba en la tablet:** sin texto se entienden peor y la barra seguía cargada.
- **Gráficos con `dragmode: 'pan'`:** sigue atrapando el dedo al hacer scroll.
- **Cambiar el componente `Tabla`:** también cambiaba Mis casos.
- **Primera columna fija en la tabla de Superponer:** cambio más chico, pero seguía con scroll lateral.

## Consecuencias
- La detección táctil (`pointer: coarse`) se hace al cargar: si se conecta un mouse, hay que recargar.
- En iPhone, Safari no permite poner un gráfico en pantalla completa: el botón no aparece.
- Los textos "Elegir" / "Sin terminar" de la casilla del Historial quedan solo para lectores de pantalla.
