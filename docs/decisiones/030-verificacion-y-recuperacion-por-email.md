# 030 — Verificación del email y recuperación de la contraseña

**Fecha:** 2026-11-14 · **Estado:** aceptada

Amplía la [004](004-autenticacion-propia.md) y la [018](018-cambio-de-contrasena.md).

## Contexto
- Cualquiera puede registrarse con un email inventado, y quien olvida su contraseña depende de que un admin corra `resetear_contrasena` en el servidor.
- La cátedra no lo pide; la entrega es la semana del 2026-11-16. Los profesores que corrijan se van a registrar: un mail que tarde o caiga en spam no puede dejarlos afuera.
- Presupuesto cero y sin dominio propio (`regelabo.duckdns.org` no permite configurar SPF/DKIM).

## Decisión
- **Verificación (RN15):** al registrarse llega un mail con un enlace. Sin verificar, la cuenta **puede iniciar sesión y recorrer el sistema, pero no pedir simulaciones** (`403 email_no_verificado`). El mail se puede reenviar desde la interfaz. El enlace vence a las **24 h**.
- **Recuperación (RN16):** "¿Olvidaste tu contraseña?" manda un mail con un enlace que vence en **1 h**. La respuesta es la misma exista o no el email (no revela quién está registrado). Poner la contraseña nueva desbloquea la cuenta y cierra todas sus sesiones, como `resetear_contrasena`. Usar el enlace también verifica el email (prueba que el usuario lo recibe).
- **Enlaces:** token aleatorio; en la base solo su hash SHA-256 (como la sesión, 013), en la tabla `enlace_email` con su tipo y vencimiento. Sirve una sola vez: se borra al usarlo. Pedir uno nuevo borra los anteriores del mismo tipo.
- **Envío:** SMTP del **Gmail del proyecto** con una contraseña de aplicación (`SMTP_*` en el `.env`). Sin `SMTP_HOST`, el mail se escribe en el log (desarrollo y tests).
- **Límites:** `olvide`, `verificar`, `recuperar` y `reenviar-verificacion` entran en el límite de 5 pedidos por minuto por IP del login (009).
- **Cuentas existentes y admins** (creados por comando) quedan verificados.

## Alternativas descartadas
| Alternativa | Por qué no |
|---|---|
| **No hacer nada** (seguir con `resetear_contrasena`) | Era viable para la cátedra, pero el equipo prefirió tenerlo. |
| **Bloquear el login sin verificar** | Un mail demorado o en spam deja afuera a quien corrige. También rompe más tests y flujos de Bruno. |
| **Brevo** (300 mails/día gratis) | Una cuenta más; con remitente `@gmail.com` enviado desde otro servidor, Gmail lo marca como spam (DMARC). |
| **Resend** | Sin dominio propio solo envía a la propia dirección. |
| **Código de 6 dígitos en vez de enlace** | Más fácil de adivinar: obliga a limitar intentos por cuenta, no solo por IP. |
| **Guardar el token en la tabla `usuario`** | Mezcla dos flujos en columnas sueltas; una tabla aparte permite el tipo y el vencimiento sin tocar el usuario. |

## Consecuencias
- El sistema depende del Gmail del proyecto: si se revoca la contraseña de aplicación, no salen mails (registrarse y entrar siguen andando; recuperar no). Gmail permite ~500 envíos por día.
- `URL_PUBLICA` en el `.env` arma el enlace; en el Codespace es la dirección `https://...app.github.dev`.
- 12 tablas en vez de 11.
