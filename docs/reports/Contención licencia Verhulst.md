# Contención de la licencia de Verhulst en el repo público

Propuesta para que el equipo decida, no una decisión tomada (`AGENTS.md`, "Reglas"). Nada de esto es asesoramiento legal: se describe lo que dice el texto de la licencia y lo que se verificó en GitHub el 20 de octubre de 2026. Para cerrar las dudas hace falta una respuesta escrita de UGent o la opinión de un abogado. No se ejecutó ningún comando de git.

## 1. Lo que se verificó hoy

**La licencia** (`backend/simulacion/verhulst/license.txt`):

- **§2:** permite *usar* el modelo y *preparar obras derivadas* solo con *non-commercial academic research purposes*. Prohíbe distribuir o sublicenciar **la obra** (*the Work*) a terceros sin autorización escrita previa de UGent.
- **§4:** permite distribuir **obras derivadas**, con el mismo fin académico no comercial, bajo cuatro condiciones:
  - (a) que se distribuyan bajo los términos de esta misma licencia, no bajo MIT;
  - (b) que cada archivo modificado avise de forma visible que se modificó;
  - (c) que se conserve este aviso textual: *"© copyright 2017 Ghent University – Universiteit Gent, all rights reserved; this Derivative work is made available for non-commercial academic research purposes and subject to an UGent Academic License (url to license)"*;
  - (d) que se incluya un NOTICE si el original lo trae. El original no lo trae.
- **§1:** las obras que siguen siendo *separables* del modelo no cuentan como obras derivadas. Es el único apoyo del texto para separar nuestro código del de UGent.
- **§3(b):** le da a UGent una licencia comercial **exclusiva** sobre las obras derivadas.

**Nuestra copia comparada con el original.** El repo oficial ([HearingTechnology/Verhulstetal2018Model](https://github.com/HearingTechnology/Verhulstetal2018Model)) tiene 26 archivos en una sola carpeta, con los perfiles comprimidos en `Poles.zip`. Nuestra copia es distinta en tres cosas:

- **Está reorganizada** en `src/core`, `src/utils`, `src/c_lib` y `data/Poles`, con los perfiles ya descomprimidos y sin los `.mat`.
- **Tiene archivos modificados.** El caso claro es `src/model2018.py`: tiene 515 líneas contra unas 330 del original, importa `PlotOrchestrator` y cambia las rutas de importación a `core.` y `utils.`. El resto de los archivos no se comparó línea por línea.
- **Tiene archivos propios del equipo:** `plot_orchestrator.py`, `diagnostic_plots.py`, `examples/orch_test.py`, `examples/quick_plot_test.py`, los `EXPLICACION.md`, `requirements.txt` y los `__init__.py`.

**Lectura del texto (no es una conclusión legal).** Los archivos que copiamos sin cambios, como `cochlea_utils.c`, los perfiles de polos y `model2018.m`, son *la obra*, y les aplica la §2. Los archivos modificados podrían entrar por la §4. Pero hoy no cumplen sus condiciones: el `LICENSE` de la raíz dice MIT para todo el repositorio, lo que choca con la §4(a), y no tienen los avisos de la §4(b) y la §4(c).

**Dónde hay copias.**

| Repositorio | Estado | ¿Tiene el código de Verhulst? |
|---|---|---|
| `facumrb/regelabo` | Público, licencia MIT, 2 forks, GitHub Pages activo | Sí, en `backend/simulacion/verhulst/` y en el historial |
| [`giani1233/regelaboForked`](https://github.com/giani1233/regelaboForked) | Fork público (creado el 22-04, último push el 09-08) | **Sí**: 109 archivos en `backend/src/simulation/Verhulst/` |
| `laucha54321/regelabo` | Fork público (16-04) | No |
| `AleF-dot/verhulst2018-wrapper` (enlazado desde el README) | Público, licencia sin declarar | No: solo trae `VERHULST_LICENSE.txt` y el código del wrapper |

GitHub Pages de regelabo publica la propuesta del proyecto ([facumrb.github.io/regelabo](https://facumrb.github.io/regelabo/)).

**Qué toca el código.** Solo dos archivos dependen de la carpeta del modelo: `backend/simulacion/motor.py:18-23` (la ruta y las importaciones) y `backend/datos/perfiles.py:19` (la ruta a `data/Poles`).

## 2. Opciones

### Opción A: aclarar las licencias (NOTICE, README y avisos de la §4)

1. Agregar un `NOTICE` en la raíz que diga que el repo es MIT **salvo** `backend/simulacion/verhulst/`, que es obra de UGent bajo su licencia académica y que no se licencia bajo MIT.
2. Agregar en cada archivo modificado un encabezado con el aviso de modificación de la §4(b) y el aviso textual de la §4(c).
3. Reescribir el `README.md` de la raíz. Hoy describe la arquitectura de servicios vieja y enlaza al wrapper. Hay que sumarle una sección de "Licencias de terceros".

| A favor | En contra |
|---|---|
| Lleva más o menos una hora y no toca ni la instalación ni la CI | **No resuelve la §2**: los archivos sin modificar se siguen distribuyendo sin autorización |
| Arregla la contradicción entre MIT y UGent, que existe con cualquier opción | Sigue dependiendo de que un TPI cuente como *academic research*, algo que el texto no define |
| Hace falta igual si UGent autoriza | Hay que editar archivos dentro de `verhulst/`. `AGENTS.md` dice que esa carpeta no se toca "salvo necesidad", y este caso lo es |

### Opción B: pasar el repo a privado

| A favor | En contra |
|---|---|
| Corta la distribución nueva en minutos, con un clic, y es reversible | **Las copias que ya están afuera siguen públicas**: GitHub separa los forks públicos y no los vuelve privados ([docs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility)). `giani1233/regelaboForked` seguiría exponiendo el modelo |
| También oculta el historial, sin reescribirlo | En GitHub Free **se despublica Pages**, donde está la propuesta del proyecto. Se puede mudar a un repo público aparte que solo tenga el sitio |
| Los docentes pueden entrar como colaboradores | Actions deja de ser gratis sin límite: quedan 2.000 minutos por mes ([docs](https://docs.github.com/en/billing/concepts/product-billing/github-actions)). Para Flake8 y pytest seguramente alcanza |
| | No se sabe si la cátedra exige que el repo sea público: el checklist está fuera del repo |
| | Choca con el "formatos abiertos" de la Visión |

### Opción C: sacar el código del repo y bajarlo del repo oficial al instalar

El repo deja de contener el modelo. Cada instalación lo baja de UGent en un commit fijo, y nuestro código queda como capa *separable* (§1). Hay dos maneras de hacerlo:

- **C1, un script de instalación (recomendada):** baja el zip del commit fijado desde GitHub, descomprime `Poles.zip` y compila `tridiag`. Se suma a `npm run install:all`.
- **C2, un submódulo de git que apunte al repo de UGent:** es más "nativo", pero suma fricción para el equipo (`--recursive`, `submodule update`), y Valentino usa fish.

Cambios concretos (estimación, sin verificar con una corrida):

1. `motor.py`: apuntar `sys.path` a la carpeta descargada y usar importaciones planas (`from get_RAM_stims import ...`).
2. `datos/perfiles.py`: leer los perfiles base de la carpeta descargada y escribir los `Custom_*` en una carpeta nuestra, fuera del código de UGent.
3. Volver al `model2018.py` original. `PlotOrchestrator` no lo necesita la app web, porque los gráficos se hacen con Plotly, y además cuesta rendimiento: lanza un hilo y genera PNG en cada corrida.
4. Mover nuestros archivos (`EXPLICACION.md`, `plot_orchestrator.py`, `diagnostic_plots.py`) a una carpeta propia, o descartarlos.
5. Incluir el SHA del commit de UGent en `VERSION_MODELO`. Esto invalida la caché una sola vez, a cambio de una procedencia exacta.
6. Hacer que la CI del paso 6 baje y compile el modelo, y actualizar `.gitignore` y los comandos de `AGENTS.md`.

| A favor | En contra |
|---|---|
| A futuro, el repo deja de distribuir la obra: quien la distribuye es UGent, desde su propio repo | Lleva más o menos uno o dos días de una persona, más una prueba de equivalencia (inferencia) |
| Nuestro código queda separable (§1), lo que baja la exposición a la exclusiva comercial de la §3(b), clave para la Visión | **No limpia el pasado**: el historial y el fork de `giani1233` siguen teniendo el código. Reescribir el historial (`git filter-repo` y un force-push) rompe los clones de los tres integrantes y no toca los forks |
| **Probablemente destraba `OHC_ind`**, porque `Poles.zip` traería los `Poles.mat`. Es una inferencia: hay que verificar el contenido del zip | Depende de que GitHub y el repo de UGent sigan disponibles al instalar. Se mitiga fijando el SHA y guardando el zip en un caché local o de la CI |
| La versión exacta del modelo queda registrada (principio de reproducibilidad) | Hay que verificar que el `model2018.py` original devuelva lo mismo que el nuestro con la misma semilla |

### Opción D: no hacer nada hasta que UGent responda

No cuesta nada, pero el repo sigue expuesto mientras tanto, y la contradicción entre MIT y UGent queda escrita. Solo tiene sentido si UGent contesta en pocos días.

## 3. Secuencia sugerida (la decide el equipo)

La evidencia apunta a **combinar opciones** en lugar de elegir una sola:

1. **Hoy:** mandar el mail a UGent (sección 4) y aplicar la **opción A**. Hace falta con cualquier respuesta y cuesta una hora.
2. **Si la cátedra no exige un repo público:** pasarlo a privado (**opción B**) como medida interina, después de mudar Pages a un repo aparte. Si lo exige, saltear este paso.
3. **Escribir a `giani1233`** para pedirle que borre el fork o lo pase a privado. Es el único lugar donde la copia está fuera de nuestro control.
4. **Antes del despliegue:** hacer la **opción C1** y registrarla como decisión 021, que es el número libre. Conviene hacerla aunque UGent autorice: separa nuestro código, fija la versión y probablemente destraba `OHC_ind`.
5. **Reescribir el historial solo si UGent lo pide.** Rompe los clones del equipo y no alcanza a los forks.

| Si UGent… | Entonces |
|---|---|
| Autoriza el uso académico y la copia pública | Con la opción A alcanza. Se guarda la autorización en `docs/decisiones/`, y la C1 queda como mejora de diseño |
| Autoriza el uso pero no la copia pública | La C1 pasa a ser obligatoria. Repo privado hasta terminarla, y evaluar la reescritura del historial |
| No responde | La C1 antes de desplegar. Un servicio web abierto queda en la zona gris de la tercera pregunta del mail |
| Niega el uso | Hay que replantear el motor del TPI con la cátedra. Es el escenario B del informe de fricción |

## 4. Borrador del mail a UGent

Va en inglés porque el destinatario está en Bélgica. **Destinataria sugerida:** Sarah Verhulst, `s.verhulst@ugent.be` (contacto publicado en el README de [CoNNear_periphery](https://github.com/HearingTechnology/CoNNear_periphery)). Ni la licencia ni el README del modelo dan un contacto de transferencia tecnológica, y por eso el mail pide que lo reenvíe si corresponde.

Antes de mandarlo hay que decidir tres cosas: quién firma, si va con copia a un docente de la cátedra (eso le da respaldo académico) y si se incluye el párrafo opcional sobre una licencia comercial. Incluirlo es más transparente, pero puede demorar o complicar la respuesta al pedido académico. Los textos entre corchetes son para completar.

```text
Subject: Permission request – Verhulstetal2018Model v1.2 in a university course project (UTN, Argentina)

Dear Prof. Verhulst,

We are a team of three students at Universidad Tecnológica Nacional, Facultad Regional
Rosario (Argentina). For the final integrative project of our course [course name]
(due end of 2026) we are building "Laboratorio Virtual Auditivo", a non-commercial
teaching web application that lets students run your 2018 model (v1.2) from an
audiogram and visualise the simulated ABR waves I/III/V, the EFR and its spectrum.
Every result is attributed to Verhulst, Altoè & Vasilkov (2018), Hearing Research
360:55–75.

We have read the UGent Academic License and want to make sure our use complies with it.
In good faith, we should also tell you that our public GitHub repository
(https://github.com/facumrb/regelabo) currently contains a copy of the model v1.2,
including a modified model2018.py (we added plotting hooks and reorganised the imports),
and that the repository's MIT license file was not scoped to exclude your code.
[We have already clarified the licensing and added the notices required by Section 4 /
We have made the repository private] while we wait for your guidance.

Could you please let us know:

1. Whether developing and presenting this university course project counts as
   "non-commercial academic research purposes" under the license.
2. Whether we may keep the model's source code (original and modified files, with the
   Section 4 notices) in our public GitHub repository, or whether you prefer that we
   remove it and have each installation download it directly from
   HearingTechnology/Verhulstetal2018Model at a pinned commit.
3. Whether we may host a free, non-commercial educational deployment in which students
   and teachers run the model through a web interface, without access to the code.
4. Whether it is acceptable that, from your published flat-loss pole profiles, we derived
   an interpolation table that maps audiogram thresholds (dB HL) to pole values.

[OPTIONAL] 5. Separately, and only for the future: whether UGent offers a licensing path
   for uses beyond academic research.

If licensing questions are handled by UGent's technology transfer office, we would be
grateful if you could forward this message or point us to the right contact. We are
happy to add any notice, citation or link you consider appropriate.

Thank you for making the model available to the research community.

Kind regards,
[Name 1], [Name 2], [Name 3]
[emails]
[Course, professor's name and email (cc)]
```

**Qué pide el mail, en castellano:**

1. Si el TPI cuenta como investigación académica no comercial.
2. Si podemos mantener el código en un repo público o si UGent prefiere que se descargue de su repo.
3. Si podemos alojar un servicio educativo gratuito.
4. Si está bien la tabla dB HL→polos que derivamos de sus perfiles (decisión 022).
5. Opcional: si hay una vía de licencia comercial a futuro.

Además el mail **reconoce de entrada** la copia y el error de la licencia MIT. Es lo correcto, y UGent puede ver el repo de todos modos: es mejor que lo lea de nuestra boca.
