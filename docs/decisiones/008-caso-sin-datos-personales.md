# 008 — "Caso" en lugar de "Paciente"

**Fecha:** 2026-10-13 · **Estado:** aceptada

## Contexto
Mientras la herramienta no sea profesional, guardar datos de personas reales genera obligaciones legales (Ley 25.326 de datos personales; Ley 26.529 de historia clínica) que no necesitamos.

## Decisión
La entidad es **Caso**: alias libre, edad y sexo opcionales, y notas. **Nada que identifique a una persona.** Los ids son UUIDv7 y cada consulta se filtra por dueño (RN4).

## Alternativas descartadas
- **Paciente con nombre y DNI desde ya.**

## Consecuencias
- **Migración futura a pacientes reales:**
  - se agrega una entidad `Paciente` (datos cifrados) relacionada 1–1 con `Caso`, sin tocar audiogramas, simulaciones ni comparaciones;
  - la integración con hospitales sería un adaptador HL7 FHIR en `controller/`;
  - antes hay que cumplir las leyes citadas: consentimiento, cifrado y registro de accesos.
