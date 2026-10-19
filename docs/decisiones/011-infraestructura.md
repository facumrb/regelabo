# 011 — Hosting y dominio

**Fecha:** 2026-10-13 · **Estado:** aceptada (provisoria)

## Contexto
El TPI exige que el sistema esté online. Una simulación necesita ~1,1 GB de RAM; con la API y el worker hacen falta al menos 2 GB, y lo cómodo son 4 GB.

## Decisión
- **DigitalOcean**, máquina x86 de 2 núcleos y 4 GB (~US$24/mes), con el crédito de US$200 del GitHub Student Pack (dura ~8 meses).
- **Dominio `.me`** gratis por 1 año (Namecheap, Student Pack).
- **Caddy** como servidor web con HTTPS automático, sirviendo frontend y API bajo el mismo dominio.
- La biblioteca C del modelo se compila dentro de la imagen Docker.

## Alternativas descartadas
- **Azure for Students** (US$100, sin tarjeta): con 4 GB dura ~3 meses. Es el plan B.
- **Oracle Cloud Always Free (ARM, 24 GB):** pide tarjeta, suele dar "out of capacity" y puede reclamar instancias ociosas.
- **Render, Railway, Heroku y Google Cloud e2-micro:** 512 MB a 1 GB, no alcanzan.

## Consecuencias
- Las ofertas del Student Pack cambian; hay que confirmarlas al activar.
