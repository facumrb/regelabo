# Informe Técnico: Proyecto de Modelo Multi-Escala de Regeneración Auditiva en la Cóclea

**Objetivo:** El proyecto busca simular regeneración de células ciliadas (*hair cells*) y neuronas auditivas en la cóclea, unificando un modelo tisular celular (CompuCell3D) con un modelo funcional auditivo (Biophysical Auditory Periphery Model), para aplicaciones en fonoaudiología.

---

## 1. Introducción y Objetivo General

El proyecto desarrolla un modelo multi-escala que simula:

- Daño coclear (por ruido, edad, ototóxicos).
- Regeneración tisular a nivel celular (proliferación, transdiferenciación de células de soporte a ciliadas, reconexión neuronal).
- Consecuencias funcionales (cómo suena el mundo después de la regeneración: audiograma simulado, discriminación en ruido, ABR/EFR).

**¿Por qué es útil en fonoaudiología?** Permite predecir clínicamente el beneficio de terapias regenerativas sin experimentos invasivos en humanos. Es el primer intento (a nuestro conocimiento) de unir un modelo *Cellular Potts Model* (CPM) con un modelo biophysical de la periferia auditiva.

El flujo es:

```
Daño + Terapia
→ Regeneración tisular (CompuCell3D)
→ Parámetros funcionales
→ Simulación auditiva (Verhulst/CoNNear)
→ Outputs clínicos
```

---

## 2. Biología Mínima de la Cóclea

*(Necesaria para entender el modelo)*

- **Células ciliadas internas (IHC):** 1 fila, responsables del 95% de la transmisión al nervio auditivo.
- **Células ciliadas externas (OHC):** 3–4 filas, amplifican el sonido (electromotilidad vía prestina).
- **Células de soporte** (Deiters, pilares, etc.): sostienen el órgano de Corti y pueden transdiferenciarse en ciliadas (en aves/peces; en mamíferos casi nulo).
- **Membrana basilar:** vibra según frecuencia (gradiente tonal: base = agudos, ápice = graves).
- **Señales clave:** Hes1/Hey1 (relojes moleculares), Atoh1 (interruptor de ciliadas), Notch (inhibición lateral), BDNF/NT-3 (reconexión neuronal).

El modelo 2024 de CompuCell3D simula el "checkerboard" (patrón alternado) mediante relojes + adhesión.

---

## 3. Modelos Base

### Modelo tisular: CompuCell3D 2024 (Rose Una & Tilmann Glimm)

*Cellular Potts Model* (CPM) que simula osciladores intracelulares (Hes1-like) + adhesión dependiente de fase para formar el patrón checkerboard en el epitelio sensorial. No incluye daño ni regeneración (es de desarrollo).

- 📄 [Paper completo](https://peerj.com/articles/16974)
- 📦 [ZIP de código (Code.zip)](https://dfzljdn9uc3pi.cloudfront.net/2024/16974/1/Code.zip)
- 💻 [Software: CompuCell3D (gratuito)](https://compucell3d.org)

### Modelo funcional: Biophysical Auditory Periphery Model (Verhulst et al. 2018) + CoNNear

Simula desde onda sonora hasta respuestas neurales (spikes, ABR, EFR). Incluye mecánica coclear, IHC, nervio auditivo y perfiles de pérdida auditiva.

- 🐍 [Versión Python original (v1.2)](https://github.com/HearingTechnology/Verhulstetal2018Model)
- ⚡ [Versión rápida CNN — recomendada (v1.0, corre en <1 s)](https://github.com/HearingTechnology/CoNNear_periphery)

---

## 4. Unificación de Ambos Modelos

Es técnicamente posible y novedosa (no existe integración publicada).
Se hace vía un pipeline Python (one-way: celular → funcional).

1. **CompuCell3D exporta métricas** (JSON/CSV): % IHC/OHC recuperadas, % checkerboard, sinapsis reconectadas, rigidez basilar.
2. Se **traducen a parámetros** de Verhulst/CoNNear (ganancia coclear, número de fibras, perfil tonotópico).
3. **CoNNear** toma un estímulo sonoro y genera outputs clínicos.

> **Utilidad clínica:** Predice si una terapia regenerativa mejora la audición real (no solo "más células").

---

## 5. Fuentes Necesarias y Setup

*(Todo descargable hoy)*

| # | Recurso | Enlace |
|---|---------|--------|
| 1 | CompuCell3D | https://compucell3d.org |
| 2 | ZIP 2024 | https://dfzljdn9uc3pi.cloudfront.net/2024/16974/1/Code.zip |
| 3 | Verhulstetal2018Model | https://github.com/HearingTechnology/Verhulstetal2018Model |
| 4 | CoNNear_periphery | https://github.com/HearingTechnology/CoNNear_periphery |
| 5 | Python 3.10+ + PyTorch | (para CoNNear) |

**Instalación:** Jupyter Notebook único que llama `cc3d.run()` y luego `connear_example.py`.

---

## 6. Vacíos y Consideraciones Importantes

- **Simplificaciones del ZIP 2024:** Modelo minimalista (solo relojes + adhesión). No incluye polaridad, quimiotaxis real, matriz extracelular ni gradiente tonal completo. Hay que agregar plugins (`Mitosis`, `CellDeath`, PDE para Atoh1/Notch/BDNF).
- **Falta de puente directo:** Debes escribir un script que traduzca métricas celulares a parámetros funcionales.
- **Tiempos:** CompuCell3D es lento (minutos–horas); CoNNear es instantáneo.
- **Validación:** Calibrar con datos de ratón/organoides (no humanos directos).
- **Licencias:** Académicas/no-comerciales (ver repos).

---

## 7. Inputs que el Modelo SÍ Puede Manejar

**Input inicial común:** Estado actual del tejido (daño % y ubicación base/ápice) + intervención regenerativa.

### Daño

- Porcentaje de IHC/OHC muertas (ej. 70% base).
- Tipo (ruido, ototóxico, edad).

### Terapias regenerativas

- **Fármacos:** Inhibidor Notch (DAPT → baja Notch, sube Atoh1).
- **Terapia génica:** AAV-Atoh1/Gfi1/Pou4f3 (sube expresión basal).
- **Células madre:** Agregar tipo "progenitor" que migra y se diferencia.
- **Combinaciones:** Fármaco + terapia génica + inmunomodulación.
- **Estimulación:** Mecánica/eléctrica (guiar diferenciación vía gradientes).

En CompuCell3D: modificás umbrales PDE o agregás tipos celulares. El modelo responde prediciendo regeneración tisular y luego outputs funcionales.

---

## 8. Inputs a los que el Modelo NO Responde Bien

> ⚠️ **Importante para uso profesional**

- Inflamación crónica / respuesta inmune (no hay macrófagos ni citocinas).
- Fibrosis/cicatrización a largo plazo.
- Variabilidad genética individual del paciente.
- Efectos > meses (envejecimiento secundario).
- Procesamiento central (tronco/corteza).
- Estimulación acústica crónica durante regeneración.
- Interacción con implante coclear.

> **Recomendación profesional:** Usa el modelo para hipótesis tempranas. Valida siempre con organoides o ensayos clínicos. No lo uses solo para decisiones FDA sin validación experimental.

---

## 9. Guía Paso a Paso para Completar el Proyecto

1. Descargar e instalar todo (ver [sección 5](#5-fuentes-necesarias-y-setup)).
2. Correr ZIP 2024 → entender checkerboard.
3. Agregar daño + regeneración en CompuCell3D (plugins `CellDeath`, `Mitosis`, PDE).
4. Exportar métricas a JSON.
5. Escribir puente Python (script maestro).
6. Correr CoNNear con parámetros derivados.
7. Analizar outputs (audiograma simulado, ABR, discriminación).
8. Extender: agregar más terapias.

---

## 10. Próximos Pasos Recomendados

- **Versión 1:** Daño + inhibidor Notch.
- **Versión 2:** Terapia génica + células madre.
- Validar con datos reales de organoides.
- Publicar como "primer modelo multi-escala de regeneración auditiva".

---

Cualquier duda, ejecutá el ZIP y el ejemplo de CoNNear primero. ¡El proyecto es reproducible y extensible! Si necesitás el script puente Python completo, avisame.

---

## Referencias Clave

*(Todas verificadas marzo 2026)*

- **PeerJ 2024:** <https://peerj.com/articles/16974>
- **Verhulst 2018:** <https://github.com/HearingTechnology/Verhulstetal2018Model>
- **CoNNear:** <https://github.com/HearingTechnology/CoNNear_periphery>
