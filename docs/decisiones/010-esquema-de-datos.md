# 010 — Detalles del esquema de datos

**Fecha:** 2026-10-14 · **Estado:** aceptada

## Decisión
- **9 tablas** creadas de una vez (la décima, `sesion`, llegó con la autenticación: ver [013](013-sesion-en-el-servidor.md)):
  - usuario, caso, audiograma, punto_audiograma;
  - simulacion, resultado_simulacion;
  - arquetipo, registro_abr, comparacion.
- **Las tablas son internas a `datos/`:** sus funciones devuelven objetos de negocio definidos en `controller/`, como pide el checklist.
- **Transacciones explícitas:**
  - `datos/` ofrece `with transaccion() as tx:` y el controller le pasa `tx` a las funciones que tienen que guardarse juntas (por ejemplo, verificar el cupo y encolar);
  - el paralelismo entre usuarios lo garantiza PostgreSQL.
- **Ids UUIDv7** generados en Python (`uuid.uuid7()`): ordenados por tiempo, eficientes en los índices y no adivinables.
- **Valores fijos** (tipo de perfil, estado, origen, gravedad, patrón): texto con `CHECK`, no `ENUM` nativo.
- **Borrado lógico de casos** (`borrado_en`): el caso se oculta y se puede recuperar. Sus simulaciones y resultados siguen sirviendo de caché.
- **Comparación:** guarda el top 3 como JSON con una copia de cada arquetipo (RN8) y una referencia opcional al arquetipo elegido (`SET NULL` si se borra).
- **Fechas** con zona horaria (`timestamptz`): se guardan como instantes y se muestran en hora de Argentina.
- **Email** en minúsculas y único.

## Alternativas descartadas
- Crear solo las tablas del sprint 0: el equipo prefirió el esquema completo desde el inicio.
- Clases ORM como objetos de negocio: atan el negocio al ORM.
- Una sesión por función sin transacciones compartidas: permite violar RN5 con un doble clic.
- UUIDv4: fragmenta los índices. ENUM nativo: migrar sus valores es incómodo.
- Borrado físico de casos: se pierden simulaciones y resultados que la caché reusa.
- Tabla intermedia comparación-arquetipo: la copia es obligatoria igual por RN8.

## Consecuencias
- El id revela cuándo se creó el registro (no es sensible porque no hay datos personales).
