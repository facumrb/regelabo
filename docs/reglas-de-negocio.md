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
| **RN11** | *(propuesta, decisión 027)* Orden de la cola: primero toda simulación con más de 10 min en cola; después por tipo de usuario (fonoaudiólogo > investigador > estudiante); dentro del tipo, quien inició menos simulaciones en los últimos 60 min; si hay empate, la más vieja. | — (es un orden) |
| **RN12** | *(propuesta, decisión 027)* Un tipo de usuario profesional (investigador o fonoaudiólogo) queda pendiente hasta que un admin lo aprueba; mientras tanto el usuario cuenta como estudiante para RN5a, RN5b y RN11. | — |
| **RN13** | *(decisión 028)* Cualquier usuario con sesión puede dejar un comentario de hasta 2000 caracteres (no vacío sin contar los espacios), hasta 5 por minuto. Solo un admin puede verlos y pasarlos entre nuevo, leído y archivado (en cualquier sentido); el autor no recibe estado ni respuesta. | 422 si el texto es inválido; 403 si un no-admin intenta verlos; 429 al pasar el límite |
| **RN14** | *(propuesta, decisión 028)* El dato `institucion_o_matricula` es obligatorio para fonoaudiólogo (matrícula) e investigador (institución), y opcional para estudiante. Es declarado: el sistema no lo verifica. Tras un rechazo (RN12), el usuario puede volver a pedir el tipo profesional una sola vez por rechazo. | 400 si falta; 409 si pide de nuevo sin rechazo previo |
| **RN15** | *(decisión 030)* Al registrarse se envía un mail de verificación (vence a las 24 h). Sin verificar el email, el usuario puede iniciar sesión pero no pedir simulaciones. | 403 `email_no_verificado` |
| **RN16** | *(decisión 030)* Quien olvida su contraseña pide un enlace por mail (vence en 1 h, un solo uso). La respuesta no revela si el email existe. La contraseña nueva desbloquea la cuenta y cierra todas sus sesiones. Si el mail no llega, el usuario puede avisar a un administrador (o el aviso es automático si el servidor no tiene SMTP), que le manda una contraseña temporal al email registrado (decisión 028). | 400 `enlace_invalido` si venció o ya se usó |

## Límites de seguridad (no son reglas de negocio)

Se implementan con `slowapi` en la capa de presentación:

- Login y registro: 5 intentos por minuto por IP. Tras 10 intentos fallidos seguidos, la cuenta queda bloqueada 15 minutos.
- API en general: 120 pedidos por minuto por usuario.
