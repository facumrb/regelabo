---
trigger: always_on
---

# Constitución del Proyecto Regelabo — Agentes

> **Versión:** 1.0 | **Fecha:** 2026-05-12

---

## 1. Propósito del Sistema de Agentes

Este directorio `.agents/` define el marco de trabajo autónomo de IA para el proyecto **Regelabo** (Laboratorio Virtual Auditivo). El sistema de agentes tiene como misión:

1. **Generar documentación técnica y de especificación** de manera consistente y reproducible.
2. **Analizar funcionalidades** contra el modelo de simulación Verhulst 2018.
3. **Asistir en el diseño** de la arquitectura de microservicios.

---

## 2. Dominio del Proyecto

**Regelabo** es un laboratorio web para fonoaudiólogos e investigadores que integra el **modelo Verhulst et al. 2018** de simulación de la vía auditiva periférica. El modelo:
- Acepta: perfil auditivo (polos de Shera), parámetros de fibras AN, estímulo acústico.
- Produce: ondas ABR (W1, W3, W5), EFR, tasas de disparo AN, velocidad BM.
- Función central: `model2018()` en Python.
- Módulo orquestador: `simulation-service` (microservicio FastAPI + Celery).

---

## 3. Reglas Globales (aplican a todos los agentes y skills)

### 3.1. Idioma
- Toda la documentación técnica se escribe en **español**.
- Los nombres de variables, funciones y archivos de código permanecen en **inglés**.

### 3.2. Consistencia con el código fuente
- Siempre referenciar parámetros y funciones reales del modelo: `model2018()`, `ohc_ind()`, `sheraP`, `nH`, `nM`, `nL`, `storeflag`, `fc`.
- No inventar APIs o funciones que no existan en `Verhulst/src/`.

### 3.3. Actor Principal
- El actor central de todos los diagramas de actividad es el **fonoaudiólogo** (usuario clínico o investigador).
- El sistema (backend, simulación, base de datos) son actores secundarios.

### 3.4. Tratamiento del Modelo Verhulst
- Por defecto, tratar el modelo como **caja negra** en los diagramas de actividad del fonoaudiólogo.
- El subdiagrama de pipeline interno es opcional y separado.
- Documentar siempre si el caso de uso requiere modificar el código interno del modelo o si puede usarlo tal cual.

### 3.5. Estructura de documentos generados
Cada funcionalidad analizada produce **dos documentos**:
- `activity-diagrams/<nombre-representativo>.md` → Diagrama de actividad y metas del fonoaudiólogo.
- `verhulst-analysis/<nombre-representativo>.md` → Análisis de uso del modelo (caja negra vs. modificación interna).

Los documentos pueden generarse en **dos comandos independientes**:
- `/speckit.diagram` para el diagrama de actividad.
- `/speckit.verhulst` para el análisis.

Ambos comandos comparten el mismo slug (`nombre-representativo`) y se vinculan entre sí mediante referencias cruzadas. Si uno de ellos se genera sin el otro, debe incluir un placeholder con la nota “Pendiente de generar por separado”.

### 3.6 Validación del analisis realizado
No se debe actualizar los mapeos de los analisis realizados, presente en 'speckit.analyze' hasta que no se acepten la creacion/cambios del mismo
---

## 4. Formato de Diagramas de Actividad

- Usar texto plano tipo UML-light (compatible con Markdown).
- Notación: `[●]` inicio/fin, `[Acción]`, `<Decisión>`, `║` barra de fork/join, `╔═══╗` caja negra.
- Incluir tabla de bifurcaciones al final.
- Respetar el nivel de abstracción: el fonoaudiólogo NO ve el interior del modelo Verhulst.

---

## 5. Formato de Análisis Verhulst

Secciones obligatorias:
1. **Veredicto**: ¿Caja negra pura / caja negra con config externa / modificación interna requerida?
2. **Entradas al modelo**: qué parámetros específicos se manipulan.
3. **Salidas del modelo**: qué outputs se consumen.
4. **Interfaz API**: qué endpoint(s) se necesitan.
5. **Consideraciones de implementación**: tiempo de cómputo, paralelismo, persistencia.

---

## 6. Referencia de Documentos Base

| Documento | Ruta | Propósito |
|---|---|---|
| Funcionalidades | `docs/specs/functionalitiesOverview.md` | Lista canónica de casos de uso |
| Análisis referencia | `docs/specs/analisisScreeningNeonatal.md` | Ejemplo de formato y profundidad esperada |
| Código Verhulst | `backend/services/simulation-service/src/Verhulst/` | Fuente de verdad técnica |
| Integración BERA-ABR | `docs/specs/Integration Points Bera Abr.md` | Puntos de integración técnica |