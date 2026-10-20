# 003 — Base de datos, entornos y backups

**Fecha:** 2026-10-13 · **Estado:** aceptada

## Contexto
El TPI pide una base SQL con acceso directo o ORM, y que el negocio siga funcionando si cambia el motor. La propuesta original usaba Supabase.

## Decisión
- **SQLAlchemy 2 + Alembic** (migraciones) con PostgreSQL, driver `psycopg` 3.
- **Dos entornos:**
  - desarrollo: PostgreSQL 17 en Docker, uno por persona (y uno descartable en CI);
  - producción: **Supabase usado solo como PostgreSQL**, sin Supabase Auth ni Storage.
- **Backup diario propio** con `pg_dump` desde GitHub Actions, porque el plan gratuito de Supabase no da backups descargables.
- Las señales (ondas, espectros) se guardan como JSON dentro de PostgreSQL.

## Alternativas descartadas
- **PostgreSQL en Docker en producción:** obliga a mantener la base y sus backups nosotros.
- **Base administrada de DigitalOcean:** ~US$15/mes del crédito; queda como plan B.
- **Cliente `supabase-py`:** ata el código a Supabase.
- **Archivos en disco para las señales:** dos fuentes de verdad y archivos huérfanos.
- **Entorno de staging:** mantenimiento de más para un equipo de 3.

## Consecuencias
- Cambiar de motor o de proveedor es cambiar `DATABASE_URL`.
- El plan gratuito de Supabase pausa proyectos sin actividad durante ~1 semana; se reactivan desde el panel.
- Límite de 500 MB en Supabase gratuito: alcanza para unas 10.000 simulaciones.
