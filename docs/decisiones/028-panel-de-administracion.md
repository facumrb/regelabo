# 028 — Panel de administración

**Fecha:** 2026-11-12 · **Estado:** propuesta (definida en una sesión de preguntas; falta implementarla)

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
