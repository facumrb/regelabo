"""
Validación del plan de análisis mediante datos sintéticos
============================================================

Este script valida el plan de análisis estadístico descrito en el paper
(GLMM binomial, enlace logit, ajustado con lme4 en R) simulando datos
sintéticos con un efecto conocido y verificando que el modelo logre
recuperarlo, tal como se plantea en el enfoque de "recovery study" /
validación de pipeline (Bolker et al., 2009, citado en el paper).

Estructura:
    1. Generación de datos sintéticos (24 participantes x 8 casos = 192 obs)
    2. Ajuste del GLMM real vía rpy2 -> lme4::glmer (misma herramienta que
       el paper, no una aproximación en Python)
    3. Repetición de la simulación N veces (parámetro), para obtener una
       tasa de recuperación del efecto (potencia empírica)
    4. Caso nulo (efecto = 0) para chequear la tasa de falsos positivos
    5. Gráficos y métricas resumen

Uso:
    python validacion_plan_analisis.py --n-repeats 500 --true-or 2.5 \
        --sigma-subject 1.0 --n-participants 24 --n-cases 8 --seed 42

Requisitos: R con el paquete lme4 instalado, y rpy2 en Python.
"""

import argparse
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr
from rpy2.robjects.conversion import localconverter

# ----------------------------------------------------------------------
# Configuración de R / lme4 (se cargan una sola vez, fuera del loop)
# ----------------------------------------------------------------------
lme4 = importr("lme4")
base = importr("base")
stats_r = importr("stats")


# ----------------------------------------------------------------------
# 1. Generación de datos sintéticos
# ----------------------------------------------------------------------
ROLES = ["estudiante", "docente", "investigador"]


def simular_datos(n_participantes, n_casos, true_log_or, sigma_sujeto,
                   intercepto_base, rng, rol_log_or=None):
    """
    Genera una tabla larga (n_participantes * n_casos filas) simulando
    la estructura descrita en el paper:

        Y_ij ~ Bernoulli(p_ij)
        logit(p_ij) = intercepto_base + beta1 * Condicion_ij
                      + beta_rol[Rol_i] + habilidad_i
        habilidad_i ~ Normal(0, sigma_sujeto)

    Rol académico (estudiante/docente/investigador) entra como efecto
    fijo ADITIVO (sin interacción con Condición), tal como especifica
    el plan de análisis actualizado del paper: "acierto ~ condicion +
    rol + (1 | participante)", sin término condicion:rol.

    Parameters
    ----------
    n_participantes : int
        Cantidad de sujetos (el paper usa 24).
    n_casos : int
        Casos por sujeto (el paper usa 8).
    true_log_or : float
        Efecto verdadero de la Condición, en escala log-odds (beta1).
        Este es el "secreto" que el GLMM debe recuperar.
    sigma_sujeto : float
        Desvío estándar del efecto aleatorio por sujeto (heterogeneidad
        de habilidad basal entre participantes).
    intercepto_base : float
        Nivel basal de acierto en log-odds bajo Condición A, rol
        "estudiante" (beta0).
    rng : np.random.Generator
        Generador de números aleatorios (para reproducibilidad).
    rol_log_or : dict o None
        Efecto aditivo (en log-odds) de cada rol respecto del nivel de
        referencia "estudiante". Default: {"estudiante": 0.0,
        "docente": 0.3, "investigador": 0.6} (investigadores/docentes
        levemente mejores en general, independiente de la condición).

    Returns
    -------
    pd.DataFrame con columnas: participante, caso, condicion, rol, acierto
    """
    if rol_log_or is None:
        rol_log_or = {"estudiante": 0.0, "docente": 0.3, "investigador": 0.6}

    mitad = n_participantes // 2
    condicion_por_sujeto = np.array([0] * mitad + [1] * (n_participantes - mitad))
    rng.shuffle(condicion_por_sujeto)

    # Rol balanceado (idealmente n_participantes múltiplo de 3, como el
    # diseño real: 8 estudiantes + 8 docentes + 8 investigadores = 24)
    base_por_rol = n_participantes // len(ROLES)
    resto = n_participantes - base_por_rol * len(ROLES)
    rol_por_sujeto = []
    for k, r in enumerate(ROLES):
        cantidad = base_por_rol + (1 if k < resto else 0)
        rol_por_sujeto += [r] * cantidad
    rol_por_sujeto = np.array(rol_por_sujeto)
    rng.shuffle(rol_por_sujeto)

    habilidad_sujeto = rng.normal(0, sigma_sujeto, size=n_participantes)

    filas = []
    for i in range(n_participantes):
        cond = condicion_por_sujeto[i]
        rol = rol_por_sujeto[i]
        logit_p = (intercepto_base + true_log_or * cond
                   + rol_log_or[rol] + habilidad_sujeto[i])
        p = 1 / (1 + np.exp(-logit_p))
        aciertos = rng.binomial(1, p, size=n_casos)
        for j in range(n_casos):
            filas.append({
                "participante": f"P{i+1:02d}",
                "caso": j + 1,
                "condicion": int(cond),
                "rol": rol,
                "acierto": int(aciertos[j]),
            })

    return pd.DataFrame(filas)


# ----------------------------------------------------------------------
# 2. Ajuste del GLMM real (lme4::glmer) vía rpy2
# ----------------------------------------------------------------------
def ajustar_glmm(df):
    """
    Ajusta el modelo:
        acierto ~ condicion + (1 | participante)
    familia binomial, enlace logit, usando lme4::glmer en R.

    Returns
    -------
    dict con: or_estimado, ic_inf, ic_sup, p_valor, convergio (bool)
    """
    with localconverter(ro.default_converter + pandas2ri.converter):
        r_df = ro.conversion.py2rpy(df)

    ro.globalenv["datos"] = r_df
    ro.globalenv["datos"] = ro.r(
        "within(datos, {condicion <- factor(condicion); "
        "rol <- factor(rol, levels = c('estudiante', 'docente', 'investigador')); "
        "participante <- factor(participante)})"
    )

    # Ajuste del modelo. Rol académico entra como efecto fijo ADITIVO
    # (con "+", no "*"): no se evalúa interacción condicion:rol, tal
    # como especifica el plan de análisis actualizado del paper.
    # suppressWarnings/suppressMessages para no inundar la salida en
    # cientos de repeticiones; los warnings de convergencia se capturan
    # aparte.
    ro.r("""
    ajuste <- tryCatch({
        withCallingHandlers({
            glmer(acierto ~ condicion + rol + (1 | participante),
                  data = datos, family = binomial(link = "logit"))
        }, warning = function(w) {
            assign("hubo_warning", TRUE, envir = .GlobalEnv)
            invokeRestart("muffleWarning")
        })
    }, error = function(e) NULL)
    """)
    ro.r("if (!exists('hubo_warning')) hubo_warning <- FALSE")

    modelo_nulo = ro.r("is.null(ajuste)")[0]
    if modelo_nulo:
        ro.r("rm(list = c('ajuste'))")
        ro.r("hubo_warning <- FALSE")
        return {"or_estimado": np.nan, "ic_inf": np.nan, "ic_sup": np.nan,
                "p_valor": np.nan, "convergio": False}

    convergio = not bool(ro.r("hubo_warning")[0])

    # Coeficiente log-odds de la condición (fila 2 = condicion1)
    coef = ro.r("summary(ajuste)$coefficients")
    log_or = coef.rx(2, 1)[0]
    p_valor = coef.rx(2, 4)[0]

    # IC 95% de Wald sobre el coeficiente (rápido, apropiado para miles
    # de repeticiones; para el análisis final del paper con datos reales
    # conviene usar confint(ajuste, method="profile") que es más preciso
    # pero mucho más lento)
    se = coef.rx(2, 2)[0]
    ic_inf_log = log_or - 1.96 * se
    ic_sup_log = log_or + 1.96 * se

    ro.r("rm(list = c('ajuste', 'hubo_warning'))")

    return {
        "or_estimado": float(np.exp(log_or)),
        "ic_inf": float(np.exp(ic_inf_log)),
        "ic_sup": float(np.exp(ic_sup_log)),
        "p_valor": float(p_valor),
        "convergio": convergio,
    }


# ----------------------------------------------------------------------
# 3. Loop de repeticiones (para un escenario con efecto real)
# ----------------------------------------------------------------------
def correr_repeticiones(n_repeats, n_participantes, n_casos, true_log_or,
                         sigma_sujeto, intercepto_base, seed, etiqueta,
                         verbose=True):
    rng = np.random.default_rng(seed)
    resultados = []

    for rep in range(n_repeats):
        df = simular_datos(n_participantes, n_casos, true_log_or,
                            sigma_sujeto, intercepto_base, rng)
        res = ajustar_glmm(df)
        res["repeticion"] = rep
        resultados.append(res)
        if verbose and (rep + 1) % max(1, n_repeats // 10) == 0:
            print(f"  [{etiqueta}] {rep + 1}/{n_repeats} repeticiones...",
                  file=sys.stderr)

    return pd.DataFrame(resultados)


# ----------------------------------------------------------------------
# 4. Métricas y gráficos
# ----------------------------------------------------------------------
def calcular_metricas(df_resultados, true_or, etiqueta):
    validos = df_resultados[df_resultados["convergio"]].copy()
    n_validos = len(validos)
    n_total = len(df_resultados)

    validos["significativo"] = (validos["ic_inf"] > 1) | (validos["ic_sup"] < 1)
    tasa_deteccion = validos["significativo"].mean() if n_validos > 0 else np.nan

    metricas = {
        "escenario": etiqueta,
        "n_repeticiones": n_total,
        "n_convergieron": n_validos,
        "tasa_convergencia": n_validos / n_total if n_total > 0 else np.nan,
        "tasa_deteccion_efecto": tasa_deteccion,
        "or_true": true_or,
        "or_estimado_promedio": validos["or_estimado"].mean(),
        "or_estimado_mediana": validos["or_estimado"].median(),
    }
    return metricas, validos


def graficar_resultados(validos_efecto, validos_nulo, true_or, out_path):
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))

    # --- Histograma de OR estimados (escenario con efecto) ---
    ax = axes[0, 0]
    ax.hist(validos_efecto["or_estimado"], bins=30, color="#4C72B0", alpha=0.8)
    ax.axvline(true_or, color="red", linestyle="--", label=f"OR verdadero = {true_or}")
    ax.axvline(1.0, color="gray", linestyle=":", label="OR = 1 (sin efecto)")
    ax.set_title("Distribución de OR estimados\n(escenario CON efecto)")
    ax.set_xlabel("Odds Ratio estimado")
    ax.set_ylabel("Frecuencia")
    ax.legend()

    # --- Forest plot (muestra de repeticiones, escenario con efecto) ---
    ax = axes[0, 1]
    muestra = validos_efecto.sort_values("or_estimado").reset_index(drop=True)
    n_mostrar = min(60, len(muestra))
    idx = np.linspace(0, len(muestra) - 1, n_mostrar).astype(int)
    muestra = muestra.iloc[idx]
    colores = np.where(muestra["significativo"], "#4C72B0", "#C44E52")
    ax.errorbar(
        muestra["or_estimado"], range(len(muestra)),
        xerr=[muestra["or_estimado"] - muestra["ic_inf"],
              muestra["ic_sup"] - muestra["or_estimado"]],
        fmt="none", ecolor=colores, alpha=0.6, elinewidth=1.2,
    )
    ax.scatter(muestra["or_estimado"], range(len(muestra)), c=colores, s=8, zorder=3)
    ax.axvline(1.0, color="black", linestyle="--", linewidth=1)
    ax.set_title(f"IC 95% por repetición (muestra de {n_mostrar})\nazul = detectó efecto, rojo = no")
    ax.set_xlabel("Odds Ratio (IC 95%)")
    ax.set_yticks([])

    # --- Comparación tasa de detección: efecto vs nulo ---
    ax = axes[1, 0]
    tasa_efecto = validos_efecto["significativo"].mean()
    tasa_nula = validos_nulo["significativo"].mean() if validos_nulo is not None else np.nan
    barras = ax.bar(
        ["Con efecto\n(potencia)", "Sin efecto\n(falsos positivos)"],
        [tasa_efecto, tasa_nula],
        color=["#4C72B0", "#C44E52"],
    )
    ax.axhline(0.05, color="gray", linestyle=":", label="5% esperado bajo H0")
    ax.axhline(0.80, color="green", linestyle=":", label="80% (potencia convencional)")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Proporción de repeticiones significativas (IC95% excluye 1)")
    ax.set_title("Tasa de detección del efecto")
    ax.legend(fontsize=8)
    for b, v in zip(barras, [tasa_efecto, tasa_nula]):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.02, f"{v:.1%}",
                ha="center", fontweight="bold")

    # --- Distribución del OR bajo el escenario nulo ---
    ax = axes[1, 1]
    if validos_nulo is not None:
        ax.hist(validos_nulo["or_estimado"], bins=30, color="#C44E52", alpha=0.8)
        ax.axvline(1.0, color="black", linestyle="--", label="OR = 1 (verdadero bajo H0)")
        ax.set_title("Distribución de OR estimados\n(escenario SIN efecto, beta1=0)")
        ax.set_xlabel("Odds Ratio estimado")
        ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close(fig)


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Validación por simulación del plan de análisis (GLMM binomial mixto vía lme4)."
    )
    parser.add_argument("--n-repeats", type=int, default=300,
                         help="Cantidad de repeticiones de la simulación (default: 300)")
    parser.add_argument("--n-participants", type=int, default=24,
                         help="Cantidad de participantes por repetición (default: 24, como el paper)")
    parser.add_argument("--n-cases", type=int, default=8,
                         help="Cantidad de casos por participante (default: 8, como el paper)")
    parser.add_argument("--true-or", type=float, default=2.5,
                         help="Odds Ratio verdadero programado para la Condición B (default: 2.5)")
    parser.add_argument("--sigma-subject", type=float, default=1.0,
                         help="Desvío estándar del efecto aleatorio por sujeto (default: 1.0)")
    parser.add_argument("--intercept", type=float, default=0.0,
                         help="Intercepto base (log-odds de acierto en Condición A) (default: 0.0)")
    parser.add_argument("--seed", type=int, default=42,
                         help="Semilla aleatoria (default: 42)")
    parser.add_argument("--skip-null", action="store_true",
                         help="Si se pasa, no corre el escenario nulo (beta1=0), solo el escenario con efecto")
    parser.add_argument("--out-prefix", type=str, default="/mnt/user-data/outputs/validacion",
                         help="Prefijo de archivos de salida (csv y png)")
    args = parser.parse_args()

    true_log_or = np.log(args.true_or)

    print(f"=== Escenario CON efecto (OR verdadero = {args.true_or}) ===", file=sys.stderr)
    df_efecto = correr_repeticiones(
        args.n_repeats, args.n_participants, args.n_cases,
        true_log_or, args.sigma_subject, args.intercept,
        seed=args.seed, etiqueta="con efecto",
    )
    metricas_efecto, validos_efecto = calcular_metricas(df_efecto, args.true_or, "con_efecto")

    validos_nulo = None
    metricas_nulo = None
    if not args.skip_null:
        print(f"=== Escenario NULO (OR verdadero = 1.0) ===", file=sys.stderr)
        df_nulo = correr_repeticiones(
            args.n_repeats, args.n_participants, args.n_cases,
            0.0, args.sigma_subject, args.intercept,
            seed=args.seed + 1, etiqueta="nulo",
        )
        metricas_nulo, validos_nulo = calcular_metricas(df_nulo, 1.0, "nulo")

    # --- Reporte por consola ---
    print("\n" + "=" * 60)
    print("RESUMEN DE VALIDACIÓN")
    print("=" * 60)
    for m in [metricas_efecto, metricas_nulo]:
        if m is None:
            continue
        print(f"\nEscenario: {m['escenario']}")
        print(f"  Repeticiones totales:      {m['n_repeticiones']}")
        print(f"  Convergieron:              {m['n_convergieron']} ({m['tasa_convergencia']:.1%})")
        print(f"  OR verdadero:              {m['or_true']:.3f}")
        print(f"  OR estimado (promedio):    {m['or_estimado_promedio']:.3f}")
        print(f"  OR estimado (mediana):     {m['or_estimado_mediana']:.3f}")
        print(f"  Tasa de detección del IC95%: {m['tasa_deteccion_efecto']:.1%}")

    # --- Guardar CSVs ---
    validos_efecto.to_csv(f"{args.out_prefix}_repeticiones_con_efecto.csv", index=False)
    resumen_rows = [metricas_efecto]
    if metricas_nulo is not None:
        validos_nulo.to_csv(f"{args.out_prefix}_repeticiones_nulo.csv", index=False)
        resumen_rows.append(metricas_nulo)
    pd.DataFrame(resumen_rows).to_csv(f"{args.out_prefix}_resumen.csv", index=False)

    # --- Gráficos ---
    graficar_resultados(validos_efecto, validos_nulo, args.true_or,
                         f"{args.out_prefix}_graficos.png")

    print(f"\nArchivos generados:")
    print(f"  {args.out_prefix}_repeticiones_con_efecto.csv")
    if metricas_nulo is not None:
        print(f"  {args.out_prefix}_repeticiones_nulo.csv")
    print(f"  {args.out_prefix}_resumen.csv")
    print(f"  {args.out_prefix}_graficos.png")


if __name__ == "__main__":
    main()