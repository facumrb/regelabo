# Reglas de negocio

Reglas acordadas para el TPI. Cada una se implementa en `backend/controller/` y tiene tests en `backend/tests/`. Los valores numéricos (cupos, umbrales, límites) van en configuración, no en el código.

| RN | Regla | Respuesta si se incumple |
|---|---|---|
| **RN1** | Un audiograma válido tiene frecuencias entre 125 y 8000 Hz, sin repetir, con valores entre −10 y 120 dB HL, e incluye obligatoriamente 500, 1000, 2000 y 4000 Hz. | 400 con el detalle del error |
| **RN2** | Gravedad según el PTA (promedio de pérdida en 500, 1000, 2000 y 4000 Hz): normal ≤ 20, leve ≤ 40, moderada ≤ 70, severa > 70 dB HL. El patrón es **con caída en agudos (descendente)** si los agudos (≥ 3 kHz) pierden ≥ 15 dB más que los graves (≤ 1 kHz); si no, es **plano** (decisión 026). | — (es un cálculo) |
| **RN3** | Parámetros de simulación válidos: nivel de 0 a 100 dB SPL; portadora de 125 a 8000 Hz; modulación de 20 a 1000 Hz; fibras nH, nM y nL enteras ≥ 0 con suma > 0 (máximos: nH 30, nM 15, nL 15); el perfil de audición tiene que existir. | 400 |
| **RN4** | Ningún usuario tiene permiso sobre casos, simulaciones o comparaciones de otro. La interfaz nunca los lista; si se intenta acceder por URL o API, se responde como si no existieran. El admin tampoco ve el contenido de casos ajenos: solo totales. | 404 (no 403, para no revelar que existen) |
| **RN5a** | Cupo de simulaciones simultáneas (en cola o ejecutando) según el tipo de usuario: estudiante 1, investigador 3, fonoaudiólogo 3. El lugar se libera cuando la simulación termina, bien o con error. | 429 |
| **RN5b** | Simulaciones nuevas por hora (ventana móvil de 60 min): estudiante 10, investigador 30, fonoaudiólogo 30. | 429 |
| **RN5c** | Tope global: si la cola del sistema tiene ≥ 20 simulaciones pendientes, se rechazan pedidos nuevos ("sistema saturado, reintentá en unos minutos"). | 503 |
| **RN6** | Un registro ABR válido tiene columnas `time` y `amplitude`, dura al menos 10 ms y está muestreado a ≥ 10 kHz. | 400 |
| **RN7** | En una comparación se muestran los 3 arquetipos más parecidos (correlación de Pearson, 0–100 %). Es **concluyente** solo si el primero supera el 70 % y le saca al menos 5 puntos al segundo; si no, se informa "resultado no concluyente". | — |
| **RN8** | Solo un admin puede crear, editar o borrar arquetipos. Cada comparación guarda una copia de los arquetipos tal como estaban al compararse, para que se pueda reproducir aunque el arquetipo cambie o se borre. | 403 para no-admin |
| **RN9** | Todo resultado de comparación incluye siempre el aviso: *"Coincidencia morfológica con un arquetipo simulado. No constituye un diagnóstico clínico."* Lo genera la capa de negocio, así que aparece también en la API y en cualquier exportación. En la interfaz se habla de **"hipótesis de estudio"** y la palabra "diagnóstico" no aparece. Al registrarse, el usuario acepta un aviso de uso no profesional y se guarda la fecha. | — |
| **RN10** | No se recalcula lo que ya se calculó: cada simulación tiene una huella (SHA-256 de perfil, fibras, estímulo, semilla y versión del modelo). Si ya existe un resultado con esa huella, se reusa al instante sin pasar por la cola, y no consume cupo (RN5). | — |

## Límites de seguridad (no son reglas de negocio)

Se implementan con `slowapi` en la capa de presentación:

- Login y registro: 5 intentos por minuto por IP. Tras 10 intentos fallidos seguidos, la cuenta queda bloqueada 15 minutos.
- API en general: 120 pedidos por minuto por usuario.
