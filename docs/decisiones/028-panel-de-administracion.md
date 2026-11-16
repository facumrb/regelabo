# 028 — Panel de administración

**Fecha:** 2026-11-12 · **Estado:** etapas 1 (comentarios) y 3 (usuarios) implementadas el 2026-11-16; etapa 2 propuesta

Completa la [009](009-roles-cupos-y-limites.md) (rol admin) y la [027](027-prioridad-en-la-cola.md) (verificación del tipo, RN12). Agrega RN13 y RN14.

## Contexto
- El admin hoy solo existe como `es_admin` y como comandos (`crear_admin`, `resetear_contrasena`); no hay ninguna pantalla para administrar.
- La 027 dejó la aprobación de tipos profesionales (RN12) para "el panel de admin".
- La revisión de fonoaudiología (decisiones 023 y 026) quedó pendiente por falta de disponibilidad: hace falta un canal para que los usuarios dejen observaciones sin depender de una reunión.
- La entrega del TPI es la semana del 2026-11-16. El panel no es obligatorio (suma al ítem opcional "Autorización (Roles)"); el despliegue sí, y va primero (decisión 029).

## Decisión
- **Dónde:** ruta `/admin` dentro de la misma app React, con una entrada "Administración" en el menú de usuario visible solo para admin. Endpoints en `/api/admin/*` protegidos con `requiere_admin`. El módulo copia la estructura de Casos (`views` → `controller` → `datos`, tests y carpeta de Bruno).
- **Aviso de pendientes:** la entrada del menú muestra un contador (tipos pendientes + comentarios sin leer). No hay envío de correos.
- **Etapas, en este orden** (cada una se entrega sola):
  1. **Comentarios (RN13).** Formulario "Dejanos un comentario o sugerencia" en `/comentarios`, desde el menú de usuario, para cualquier usuario con sesión: un solo campo de texto de hasta 2000 caracteres. Al enviar se muestra "¡Gracias!" y nada más: el autor no ve estados ni respuestas, para no prometer una devolución. En el panel, el admin los lista, los marca como **leídos** o **archivados** y los filtra por tipo de usuario (para ver primero los de fonoaudiólogos). Nadie más los ve.
  2. **Aprobación de tipos (RN12 y RN14).** Solo si sobra tiempo antes de la entrega.
     - El registro suma un campo `institucion_o_matricula` con distinta etiqueta según el tipo (RN14). El sistema no lo valida contra ningún registro: el admin lo mira y decide.
     - El panel lista los pendientes con ese dato y permite **aprobar** o **rechazar** con un motivo opcional.
     - Si se rechaza, el usuario pasa a estudiante y ve el motivo en *Mi cuenta*; desde ahí puede volver a pedir el tipo una vez por cada rechazo.
  3. **Usuarios.** Después de la entrega. Lista con tipo, estado y totales (cantidad de casos y simulaciones, sin contenido, por RN4); **desbloquear** y **resetear contraseña** reusando lo que hacen los comandos. Dar o quitar admin sigue siendo solo por comando, para que un admin no pueda dejar el sistema sin admins.
- **Fuera del panel por ahora:** cola y worker (cancelar simulaciones), arquetipos (RN8, el módulo no existe), catálogo de perfiles y estadísticas generales.

## Detalles de la etapa 1 (2026-11-16)
- **Estados libres:** el admin pasa un comentario entre nuevo, leído y archivado en cualquier sentido, así un clic por error se corrige solo.
- **Lista:** sin filtro de estado se ven los nuevos y los leídos (no los archivados), del más nuevo al más viejo, paginados por cursor. Filtros opcionales por estado y por tipo de usuario. Cada comentario muestra nombre, tipo y email del autor.
- **Spam:** hasta 5 comentarios por minuto. Se cuenta por sesión (la cookie), no por IP, porque en Codespaces todos llegan desde el mismo proxy.
- **Contador:** `GET /api/admin/pendientes`, pedido al cargar la app, al cambiar de pantalla y después de cada acción del panel. Se muestra sobre el avatar y junto a *Administración*. *Cambio del 2026-11-16:* también cada 60 segundos, solo para admin y solo con la pestaña a la vista (y al volver a ella), para que un pedido nuevo aparezca sin navegar; las notificaciones empujadas por el servidor (WebSocket, SSE) se descartaron por ser infraestructura de más para un contador.
- **Texto inválido:** 422, como el resto de los errores de formato de la API (decisión 014), no 400.
- **Endpoints:** `POST /api/comentarios` (204, sin cuerpo: el autor no recibe nada), `GET /api/admin/comentarios`, `PATCH /api/admin/comentarios/{id}` y `GET /api/admin/pendientes`.

## Ajuste de la etapa 3 (2026-11-16)
- **Se adelantó la etapa 3 antes de la entrega, y la 2 pasa a después.** La 3 reusa lógica que ya existía (`resetear_contrasena`, `reiniciar_intentos`, `marcar_verificado`) y resuelve un problema del despliegue. La 2 toca el registro, *Mi cuenta* y los cupos, y conviene hacerla junto con la [027](027-prioridad-en-la-cola.md).
- **Verificar el email a mano** (suma a la [030](030-verificacion-y-recuperacion-por-email.md)): si el mail no llega o el SMTP no está configurado, el usuario queda sin poder simular (RN15). El admin lo destraba sin tocar la base.
- **Pedido de restablecimiento:** primero va el enlace automático de "¿Olvidaste tu contraseña?" (RN16). El pedido al admin (`usuario.restablecimiento_pedido_en`) se crea solo si el usuario toca "¿No te llegó el mail? Avisar a un administrador" (`POST /api/auth/olvide/avisar-admin`, mismo límite y misma respuesta exista o no la cuenta), o directo si el servidor no tiene SMTP. Se descartaron crear siempre el pedido (con SMTP, el usuario recibía dos mails: el enlace y la temporal del admin) y crearlo solo sin SMTP (si el mail se va a spam, el usuario no tendría cómo avisar). Los pedidos suman al contador del menú y aparecen arriba de la lista de usuarios, en amarillo. El pedido se da por atendido cuando la contraseña cambia por cualquier camino: temporal, enlace del mail o *Mi cuenta*. La respuesta sigue siendo la misma exista o no la cuenta.
- **Contraseña temporal, solo con pedido** (409 `sin_pedido_de_restablecimiento` si no lo hay): el sistema genera una al azar de 16 caracteres; también desbloquea la cuenta y cierra todas sus sesiones, igual que el comando. No se muestra en pantalla: un botón abre el programa de correo del admin con un mail ya escrito al **email registrado** de la cuenta, con la temporal adentro. Así solo la recibe el dueño del email, aunque el pedido lo haya hecho otra persona, y no hace falta SMTP en el servidor. Se descartaron: mostrarla para que el admin la pase por otro medio (el admin podría dársela a quien se hace pasar por el usuario), mandarla por el SMTP del servidor (si funciona, ya alcanza con el enlace de RN16) y que el admin la escriba.
- **Otros admin:** el panel no aplica ninguna acción sobre otros admin (403 `usuario_es_admin`); se manejan por comando. Así, si roban una cuenta de admin, no se puede tomar las demás.
- **Lista:** búsqueda por parte del email o del nombre y filtro por tipo, paginada por cursor. Muestra alta, cantidad de casos (sin los borrados) y de simulaciones, si el email está verificado y si la cuenta está bloqueada. El contador del menú suma comentarios nuevos y pedidos de restablecimiento; las cuentas bloqueadas no suman (el bloqueo se va solo a los 15 minutos).
- **Endpoints:** `GET /api/admin/usuarios` (con `con_pedido=true`, solo los pedidos) y `POST /api/admin/usuarios/{id}/desbloquear`, `/verificar-email` y `/resetear-contrasena`.

## Alternativas descartadas
- **App de administración aparte:** duplica sesión, despliegue y estilos sin ganar nada.
- **Sugerencias con estados visibles para el autor** (pendiente/aceptada/rechazada con respuesta): da a entender que siempre habrá devolución, y el equipo no puede garantizarla.
- **Comentarios solo para fonoaudiólogos aprobados:** un estudiante que reporta un error también aporta; el filtro por tipo ya deja ver primero a los profesionales.
- **Comentarios sobre temas fijos** (terminología, contenido del modelo): el texto libre cubre todo con un solo campo.
- **Aprobar sin ningún dato del usuario:** el admin no tendría con qué decidir.
- **Verificar la matrícula contra el registro del colegio profesional:** fuera del alcance del TPI (como dice la 027); el dato es declarado.
- **Gestionar la cola, los arquetipos o el catálogo desde el panel:** la cancelación con el worker en ejecución es la parte más riesgosa, los arquetipos dependen de un módulo que no existe y el catálogo puede cambiarse a partir de los comentarios.
- **Dar o quitar admin desde el panel:** un admin podría quitarse el rol a sí mismo o a todos.

## Consecuencias
- Tabla nueva `comentario` (usuario, texto, fecha, estado `nuevo`/`leido`/`archivado`) y su migración.
- La etapa 2 suma a `usuario` el campo `institucion_o_matricula`, el estado de verificación y el motivo de rechazo (además de lo que pide la 027); los usuarios existentes quedan verificados en la migración.
- Hasta que exista la etapa 2, la aprobación se hace con un comando (como prevé la 027).
- El `RequiereSesion` del frontend necesita una variante para admin, o la página `/admin` revisa `es_admin` del usuario de la sesión.
- Al sumar el módulo hay que agregar su carpeta en `docs/api/` (copiando `4-casos`).
