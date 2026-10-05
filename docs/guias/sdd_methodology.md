# SDD + Antigravity orientado a servicios

## 1. Proposito

Esta guia define una forma de trabajo concreta para usar SDD + Antigravity por servicio dentro de `Laboratorio`.

El objetivo es reducir ambiguedad antes de implementar, mantener el alcance controlado y revisar lo generado por IA contra una especificacion minima por servicio.

No describe una estructura SDD ya instalada en el repositorio. Donde no exista evidencia en el repo, esta guia lo marca como `convencion recomendada`.

## 2. Contexto validado del proyecto

Hoy el proyecto muestra una orientacion a servicios en `regelabo/README.md` y en la separacion tecnica visible en `regelabo/backend/src`.

Contexto verificado:

- `regelabo/frontend/`: capa de interfaz.
- `regelabo/backend/src/api`: entrada HTTP y capa de API.
- `regelabo/backend/src/db`: acceso a datos.
- `regelabo/backend/src/simulation`: simulacion cientifica.
- `regelabo/backend/src/llm`: analisis e integracion con LLM.
- `regelabo/backend/src/services`: capa de servicios compartidos.

Tambien estan verificados los scripts actuales de trabajo en `regelabo/package.json`: `install:all`, `dev:backend`, `dev:frontend` y `dev`.

No se encontro en el repo una estructura SDD por servicio, ni carpetas propias de Antigravity u OpenSpec, ni un catalogo verificable de slash commands. Por eso esta guia evita afirmar comandos slash como disponibles hoy.

## 3. Que es un servicio en este proyecto

En este proyecto, un servicio es una unidad funcional con una sola responsabilidad dominante, entradas definidas, salidas definidas y limites claros.

Un servicio bien definido:

- resuelve una necesidad puntual;
- no absorbe responsabilidades de otras areas;
- puede describirse en una frase;
- deja explicito que recibe, que devuelve y que errores maneja.

Si no se puede explicar en una frase, el alcance probablemente esta mal cortado.

## 4. Cuando conviene aplicar SDD + Antigravity

Este enfoque conviene cuando:

- se crea un servicio nuevo;
- se altera el comportamiento de un servicio relevante;
- hay integraciones entre varias partes del sistema;
- existen reglas de negocio, validaciones o casos limite que no conviene dejar implicitos.

No conviene empezar por pedir codigo directo. Primero hay que fijar el comportamiento del servicio. Despues se planifica. Recien en ese punto se implementa.

## 5. Estructura por servicio

`Convencion recomendada`:

```text
<servicio>/
  README.md
  requirements.md
  contracts.md
  rules.md
  plan.md
  tasks.md
```

Esta estructura no esta verificada como implementada hoy en `Laboratorio`. Se propone como base minima para trabajar por servicio sin mezclar especificacion, diseno y ejecucion.

## 6. Contenido minimo de cada archivo

### `README.md`

Define identidad y frontera del servicio:

- nombre del servicio;
- problema que resuelve;
- responsabilidad principal;
- relacion con otros servicios o modulos.

### `requirements.md`

Define que debe lograr el servicio:

- objetivo;
- alcance;
- fuera de alcance;
- restricciones;
- dependencias relevantes.

### `contracts.md`

Define la interfaz funcional:

- entradas;
- salidas;
- errores esperados;
- formatos, campos obligatorios y supuestos de integracion.

### `rules.md`

Define comportamiento que no debe romperse:

- reglas de negocio;
- validaciones;
- invariantes;
- casos limite.

### `plan.md`

Define la estrategia tecnica antes de tocar codigo:

- enfoque tecnico;
- modulos o archivos a intervenir;
- riesgos;
- orden de implementacion;
- decisiones abiertas.

### `tasks.md`

Define ejecucion verificable:

- tareas cortas y observables;
- una tarea por cambio comprobable;
- orden de trabajo sugerido;
- criterio de cierre implicito en cada punto.

## 7. Flujo de trabajo recomendado

Secuencia recomendada por servicio:

1. Delimitar un solo servicio.
2. Completar `README.md`, `requirements.md`, `contracts.md` y `rules.md`.
3. Pedir a Antigravity analisis y orden del trabajo antes de implementar.
4. Revisar `plan.md` y ajustar decisiones abiertas.
5. Revisar `tasks.md` hasta que cada tarea sea concreta y verificable.
6. Implementar por tramos acotados.
7. Comparar el resultado contra contratos, reglas y alcance.
8. Actualizar la documentacion del servicio si cambio el comportamiento acordado.

Regla practica: si la especificacion es ambigua, la IA completa huecos. Mejor contexto produce menos desvio y menos retrabajo.

## 8. Como pedir trabajo a Antigravity sin inventar arquitectura

Un pedido util:

- nombra un solo servicio;
- aclara objetivo y fuera de alcance;
- marca los archivos del servicio como fuente de verdad;
- pide analisis, plan y tareas antes de implementar;
- exige que se expliciten dudas si falta contexto.

Ejemplo de prompt de trabajo:

> Trabajemos sobre `<servicio>`. Usa como fuente de verdad `README.md`, `requirements.md`, `contracts.md` y `rules.md`. Primero ordena el trabajo en un `plan.md` y un `tasks.md`. No propongas implementaciones fuera del alcance definido. Si falta informacion, marcala antes de avanzar.

Este ejemplo evita mencionar slash commands no verificados y se apoya solo en artefactos documentales que si pueden existir por convencion.

## 9. Ejemplo de referencia

`Convencion recomendada`: usar un servicio conceptual como `simulation-runner-service` para documentar cambios sobre la capacidad de simulacion.

Ese nombre no esta verificado hoy como carpeta real del repo. Sirve solo como ejemplo de redaccion por servicio, alineado con la existencia de `regelabo/backend/src/simulation`.

Contenido minimo esperado:

### `README.md`

- inicia simulaciones auditivas a partir de entradas ya validadas;
- no valida archivos crudos;
- no genera visualizaciones finales.

### `requirements.md`

- recibe referencia a un audiograma valido;
- recibe parametros de simulacion;
- crea un registro inicial;
- inicia la ejecucion;
- devuelve identificador y estado inicial;
- deja fuera de alcance interpretacion clinica, autenticacion y graficos finales.

### `contracts.md`

- entrada minima: `user_id`, `audiogram_id`, `simulation_parameters`;
- salida exitosa: `simulation_id`, `status`, `created_at`, `message`;
- salida de error: `error_code`, `message`.

### `rules.md`

- no iniciar sin parametros obligatorios;
- no iniciar si el audiograma no existe o no es valido;
- asociar cada simulacion a un usuario;
- registrar errores;
- no modificar el audiograma original.

### `plan.md`

- definir punto de entrada;
- definir persistencia inicial;
- definir invocacion al motor de simulacion;
- definir manejo de errores y consulta de estado.

### `tasks.md`

- formalizar contrato de entrada y salida;
- implementar inicio de simulacion;
- persistir estado inicial;
- cubrir errores esperados;
- exponer consulta de estado;
- agregar pruebas basicas.

## 10. Criterios de revision

Antes de aceptar una salida generada con IA, revisar:

- que el servicio siga teniendo una sola responsabilidad;
- que se implemente solo lo pedido;
- que entradas, salidas y errores coincidan con `contracts.md`;
- que el comportamiento respete `rules.md`;
- que el codigo refleje `plan.md` y `tasks.md`;
- que no aparezca arquitectura inventada;
- que el resultado sea mantenible y verificable.

Si el codigo y la especificacion divergen, primero se corrige la especificacion o el pedido. Parchear sin cerrar esa brecha solo mueve el problema.

## 11. Checklist final

- [ ] El servicio se explica en una frase.
- [ ] El alcance y el fuera de alcance estan cerrados.
- [ ] Entradas, salidas y errores estan definidos.
- [ ] Las reglas de negocio estan explicitadas.
- [ ] El plan tecnico esta acotado.
- [ ] Las tareas son concretas y verificables.
- [ ] El pedido a Antigravity usa documentacion del servicio como contexto.
- [ ] La salida final fue revisada contra la documentacion del servicio.
