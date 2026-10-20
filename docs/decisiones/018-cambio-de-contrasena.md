# 018 — Cambio de contraseña

**Fecha:** 2026-10-16 · **Estado:** aceptada

## Decisión
- **Con la sesión iniciada:** `POST /api/auth/contrasena` con `{"actual", "nueva"}`; responde 204. Pantalla "Mi cuenta" (`/cuenta`), a la que se llega con un clic en el nombre del usuario en la barra.
- **Se pide la contraseña actual**, para que alguien que encuentre una sesión abierta no pueda quedarse con la cuenta. La repetición de la nueva se controla solo en la pantalla.
- **Una actual incorrecta** responde `contrasena_actual_incorrecta` (400, no 401: el frontend no debe entender "se cerró la sesión") y **suma al contador de fallos del login**; a los 10, la cuenta se bloquea 15 minutos. Además aplica el límite de 5 pedidos por minuto por IP.
- **La nueva:** entre 8 y 128 caracteres (`contrasena_invalida`) y distinta de la actual (`contrasena_repetida`), ambos 400. Sin reglas de complejidad: se prioriza el largo, como en el registro.
- **En una sola transacción:** se guarda el hash argon2id de la nueva, se reinicia el contador de fallos y se **cierran todas las demás sesiones** del usuario; la actual sigue.
- **Reseteo por el admin:** `uv run python -m backend.comandos.resetear_contrasena` pone una contraseña nueva, desbloquea la cuenta y cierra todas sus sesiones.

## Alternativas descartadas
- **"Olvidé mi contraseña" por email:** necesita un servicio de correo, tokens de un solo uso con vencimiento y otra pantalla. Queda para cuando haya despliegue; mientras tanto, el comando del admin.
- **Cerrar también la sesión actual:** obliga a volver a entrar sin ganar seguridad (quien cambia la contraseña ya demostró conocer la actual).
- **No cerrar ninguna sesión:** quien robó la contraseña seguiría adentro después del cambio.

## Consecuencias
- Mejora anotada: re-hashear en el login si cambian los parámetros de argon2 (`check_needs_rehash`).
