"""
Validación numérica de métricas de análisis secundarios
========================================================

Este script valida, mediante pruebas unitarias con datos sintéticos y
casos conocidos (ground truth), el cálculo correcto de dos métricas
descriptas en el plan de análisis del paper (Sección "Análisis
secundarios" del LaTeX):

    1. Puntuación de Brier (calibración de la confianza subjetiva).
       Ec. 2 del plan:
           Brier = (1/N) * sum_ij (p^subj_ij - Y_ij)^2

    2. Estadístico kappa-w lineal de Cohen (acuerdo interevaluador
       para la codificación de la explicación causal X_ij en 4
       categorías 0..3).
       Ec. 3 del plan:
           kappa_w = 1 - (sum_kl w_kl * p_kl) / (sum_kl w_kl * e_kl)
           con   w_kl propto |k - l|   (pesos lineales / iguales).

Estructura:
    A. Pruebas de caja cerrada (ground truth): casos pequeños donde
       el valor de Brier y kappa_w puede calcularse a mano y se
       compara contra la implementación (tolerancia 1e-9).
    B. Pruebas de consistencia / propiedades matemáticas:
       - Caso de acuerdo perfecto -> kappa_w = 1
       - Caso de acuerdo esperable por azar uniforme -> kappa_w ~ 0
       - Brier con predicciones perfectas -> Brier = 0
       - Brier con predicciones totalmente erróneas -> Brier = 1
    C. Prueba de concordancia con una implementación de referencia
       independiente (cuando `scikit-learn` esté disponible), en el
       mismo espíritu que el control de calidad descrito en el plan
       (dos rutas independientes, diferencia relativa < 1e-6).
    D. Reporte por consola con formato [OK] / [ERROR] (ASCII, apto
       para terminal de Windows).

Uso:
    python prueba2.py

Requisitos (solo para la prueba C, opcional): scikit-learn.
Si sklearn no está instalado, las pruebas A y B se ejecutan igual y
la prueba C se marca como SKIP.
"""

import sys
import numpy as np

# ---------------------------------------------------------------------
# 1. Implementación de referencia (ruta "b": fórmulas matemáticas)
# ---------------------------------------------------------------------

def brier_score(p_subj, y):
    """
    Calcula la puntuación de Brier (Ec. 2 del plan).

    Parameters
    ----------
    p_subj : array-like de float, shape (N,) o (N, M)
        Probabilidad subjetiva p^subj_ij en [0, 1].
    y : array-like de int/float, mismo shape que p_subj
        Variable binaria Y_ij en {0, 1}.

    Returns
    -------
    float, valor de Brier.
    """
    p = np.asarray(p_subj, dtype=float)
    yy = np.asarray(y, dtype=float)
    if p.shape != yy.shape:
        raise ValueError("p_subj e y deben tener la misma forma.")
    if np.any((p < 0) | (p > 1)):
        raise ValueError("p_subj contiene valores fuera de [0, 1].")
    return float(np.mean((p - yy) ** 2))

def kappa_w_lineal(rater1, rater2, categorias=(0, 1, 2, 3)):
    """
    Calcula el estadístico kappa-w lineal de Cohen (Ec. 3 del plan).

    w_kl ∝ |k - l|. Se usa la versión normalizada tal que
    w_kl = |k - l| / (|C| - 1), donde C es el conjunto de categorías;
    esto hace que max(w_kl) = 1 y es equivalente a los "equal" /
    "linear weights" habituales en la literatura (el cociente de
    kappa_w es invariante a la escala de w, siempre que sean
    proporcionales a |k-l|).

    Parameters
    ----------
    rater1, rater2 : array-like de enteros, misma longitud
        Calificaciones (valores en categorias) de cada juez.
    categorias : iterable ordenable
        Conjunto de categorías posibles. El orden importa.

    Returns
    -------
    float, valor de kappa_w entre -inf y 1.
    """
    r1 = np.asarray(rater1)
    r2 = np.asarray(rater2)
    if r1.shape != r2.shape or r1.ndim != 1:
        raise ValueError("rater1 y rater2 deben ser vectores de igual longitud.")

    cats = np.asarray(sorted(categorias))
    nc = len(cats)
    idx = {cat: k for k, cat in enumerate(cats)}

    # Matriz de observaciones p_kl (proporciones)
    mat_abs = np.zeros((nc, nc), dtype=float)
    for a, b in zip(r1, r2):
        if a not in idx or b not in idx:
            raise ValueError(
                f"Calificación ({a}, {b}) fuera de las categorías {list(cats)}."
            )
        mat_abs[idx[a], idx[b]] += 1.0
    n_total = mat_abs.sum()
    if n_total == 0:
        return np.nan
    P = mat_abs / n_total           # p_kl

    # Márgenes
    p_k_dot = P.sum(axis=1)         # p_{k.}
    p_dot_l = P.sum(axis=0)         # p_{.l}
    E = np.outer(p_k_dot, p_dot_l)  # e_kl

    # Pesos lineales: w_kl = |k - l| / (nc - 1)
    grid = np.arange(nc)
    W = np.abs(grid[:, None] - grid[None, :])
    if nc > 1:
        W = W / (nc - 1)

    num = (W * P).sum()
    den = (W * E).sum()

    if den == 0:
        return 1.0 if num == 0 else np.nan
    return float(1.0 - num / den)

# ---------------------------------------------------------------------
# 2. Implementación alternativa (ruta "a": sklearn, si está disponible)
# ---------------------------------------------------------------------

try:
    from sklearn.metrics import (
        brier_score_loss,
        cohen_kappa_score,
    )
    HAS_SKLEARN = True
except Exception:
    HAS_SKLEARN = False

def brier_score_sklearn(p_subj, y):
    """Brier vía sklearn (la API recibe y primero, luego probas)."""
    return float(brier_score_loss(y, p_subj))

def kappa_w_sklearn(rater1, rater2, categorias=(0, 1, 2, 3)):
    """Kappa lineal de Cohen vía sklearn."""
    return float(cohen_kappa_score(rater1, rater2,
                                   labels=list(categorias),
                                   weights="linear"))

# ---------------------------------------------------------------------
# 3. Runner de pruebas
# ---------------------------------------------------------------------

TOL_ABS = 1e-9
TOL_REL_CONCORDANCIA = 1e-6

_resultados = []

def _marcar(nombre, ok, extra=""):
    tag = "[OK]   " if ok else "[ERROR]"
    linea = f"{tag} {nombre}"
    if extra:
        linea += f"  ({extra})"
    print(linea)
    _resultados.append((nombre, ok))

def correr_pruebas():
    print("=" * 65)
    print("VALIDACIÓN NUMÉRICA: Brier score + kappa-w lineal")
    print("=" * 65)

    # ===================== A. PRUEBAS DE CAJA CERRADA =====================
    print("\n-- A. Pruebas de caja cerrada (ground truth a mano) --\n")

    # --- Brier: caso trivial perfecto ---
    p = np.array([0.0, 0.0, 1.0, 1.0])
    y = np.array([0,    0,   1,   1])
    b = brier_score(p, y)
    _marcar("Brier / predicciones perfectas  -> 0",
            np.isclose(b, 0.0, atol=TOL_ABS),
            f"B={b:.3e}")

    # --- Brier: caso totalmente erróneo ---
    p = np.array([1.0, 1.0, 0.0, 0.0])
    y = np.array([0,   0,   1,   1])
    b = brier_score(p, y)
    _marcar("Brier / predicciones todo mal   -> 1",
            np.isclose(b, 1.0, atol=TOL_ABS),
            f"B={b:.3e}")

    # --- Brier: ejemplo concreto calculado a mano ---
    # [(0.2, 0), (0.8, 1), (0.5, 0)]
    # = (1/3) * [ (0.2)^2 + (-0.2)^2 + (0.5)^2 ]
    # = (1/3) * [ 0.04 + 0.04 + 0.25 ] = 0.33 / 3 = 0.11
    p = np.array([0.2, 0.8, 0.5])
    y = np.array([0,   1,   0])
    b = brier_score(p, y)
    esperado = 0.11
    _marcar("Brier / ejemplo a mano           -> 0.11",
            np.isclose(b, esperado, atol=TOL_ABS),
            f"B={b:.10f}  (esperado {esperado})")

    # --- Kappa-w: acuerdo perfecto en 4 categorías ---
    r1 = [0, 1, 2, 3, 0, 1, 2, 3, 2, 2]
    r2 = list(r1)
    k = kappa_w_lineal(r1, r2)
    _marcar("Kappa-w / acuerdo perfecto      -> 1",
            np.isclose(k, 1.0, atol=TOL_ABS),
            f"K={k:.10f}")

    # --- Kappa-w: matriz 2x2 muy simple, ejemplo manual ---
    # 2 categorías 0,1. 8 items: 3 (0,0) + 1 (0,1) + 1 (1,0) + 3 (1,1)
    # P = [[3/8, 1/8],
    #      [1/8, 3/8]]
    # W (lineal normalizado nc=2): [[0, 1], [1, 0]]
    # num = W·P = (1/8+1/8) = 0.25
    # p_k_dot = [0.5, 0.5] ; E = [[0.25, 0.25], [0.25, 0.25]]
    # den = W·E = 0.5
    # kappa = 1 - 0.25 / 0.50 = 0.5
    r1 = [0]*3 + [0]*1 + [1]*1 + [1]*3
    r2 = [0]*3 + [1]*1 + [0]*1 + [1]*3
    k = kappa_w_lineal(r1, r2, categorias=(0, 1))
    _marcar("Kappa-w / ejemplo 2x2 a mano    -> 0.5",
            np.isclose(k, 0.5, atol=TOL_ABS),
            f"K={k:.10f}  (esperado 0.5)")

    # --- Kappa-w: sin acuerdo útil (distribuciones marginales uniformes,
    # caso extremo donde p_kl es la matriz "encontrada" simétrica que
    # hace num/den → 1) -> kappa = 0 si p_kl = e_kl exactamente
    # Construcción: 4 categorías, n=16, uniforme en todas las celdas
    r1 = []; r2 = []
    for a in (0, 1, 2, 3):
        for b in (0, 1, 2, 3):
            r1.append(a); r2.append(b)
    k = kappa_w_lineal(r1, r2)
    # Acá p_kl es uniforme 1/16 y e_kl también es 1/16 porque los
    # márgenes son [0.25, 0.25, 0.25, 0.25]. Entonces num=den y k=0.
    _marcar("Kappa-w / tabla uniforme        -> 0",
            np.isclose(k, 0.0, atol=TOL_ABS),
            f"K={k:.10f}")

    # ===================== B. PROPIEDADES MATEMÁTICAS ======================
    print("\n-- B. Pruebas de propiedades matemáticas --\n")

    # Permutar categorías con la misma calificación: kappa invariante
    # (si se re-codifica sin alterar los pares y las categorías son las
    # mismas, el resultado es igual). Caso: replicar items y permutar
    # el orden del input (no de las categorías).
    datos = [(0, 1), (1, 2), (2, 3), (3, 0), (1, 1), (2, 2), (0, 2)]
    rA, rB = zip(*datos)
    orden = [6, 3, 0, 5, 1, 2, 4]
    rA2 = [rA[i] for i in orden]
    rB2 = [rB[i] for i in orden]
    k1 = kappa_w_lineal(rA, rB)
    k2 = kappa_w_lineal(rA2, rB2)
    _marcar("Kappa-w / invariante a permutación de filas",
            np.isclose(k1, k2, atol=TOL_ABS),
            f"K1={k1:.6e}  K2={k2:.6e}")

    # Brier es invariante a permutar filas de la misma forma
    np.random.seed(0)
    pp = np.random.rand(50)
    yy = np.random.randint(0, 2, size=50)
    perm = np.random.permutation(50)
    b1 = brier_score(pp, yy)
    b2 = brier_score(pp[perm], yy[perm])
    _marcar("Brier   / invariante a permutación de pares",
            np.isclose(b1, b2, atol=TOL_ABS),
            f"B1={b1:.6e}  B2={b2:.6e}")

    # Brier con forma (N, M) aplanada debe dar igual que (N*M,)
    pp2d = pp.reshape(5, 10)
    yy2d = yy.reshape(5, 10)
    b_2d = brier_score(pp2d, yy2d)
    _marcar("Brier   / resultado igual 1D vs 2D",
            np.isclose(b1, b_2d, atol=TOL_ABS),
            f"B_1D={b1:.6e}  B_2D={b_2d:.6e}")

    # Kappa con un desacuerdo de magnitud 1 vs un desacuerdo de magnitud
    # 3: kappa debe ser mayor (menor penalización total) en el primer
    # caso.
    # Caso 1: 9 acuerdos + 1 desacuerdo (0,1)  -> distancia 1
    base_acuerdo = [(c, c) for c in [0, 1, 2, 3] for _ in range(2)]  # 8
    base_acuerdo += [(0, 0), (1, 1)]                                  # +2 = 10
    d1 = base_acuerdo + [(0, 1)]
    d3 = base_acuerdo + [(0, 3)]
    r1_d1, r2_d1 = zip(*d1)
    r1_d3, r2_d3 = zip(*d3)
    k_d1 = kappa_w_lineal(r1_d1, r2_d1)
    k_d3 = kappa_w_lineal(r1_d3, r2_d3)
    _marcar("Kappa-w / desacuerdo grande (|k-l|=3) penaliza más que el chico (|k-l|=1)",
            k_d1 > k_d3,
            f"K(|1|)={k_d1:.4f} > K(|3|)={k_d3:.4f} ? {k_d1 > k_d3}")

    # ===================== C. CONCORDANCIA CON SKLEARN =====================
    print("\n-- C. Concordancia con implementación independiente (sklearn) --\n")

    if not HAS_SKLEARN:
        print("[SKIP] scikit-learn no está instalado. Se saltea esta sección.")
        print("       Para ejecutarla: pip install scikit-learn")
    else:
        # --- Brier contra sklearn, datos aleatorios ---
        rng = np.random.default_rng(123)
        for _ in range(5):
            n = rng.integers(20, 300)
            pp = rng.uniform(0, 1, size=n)
            yy = rng.integers(0, 2, size=n)
            b_our = brier_score(pp, yy)
            b_skl = brier_score_sklearn(pp, yy)
            ok = abs(b_our - b_skl) / max(abs(b_skl), 1e-12) < TOL_REL_CONCORDANCIA
            _marcar(f"Brier   / muestra n={n}", ok,
                    f"nuestro={b_our:.6e}  sklearn={b_skl:.6e}")
            if not ok:
                break

        # --- Kappa-w contra sklearn, datos aleatorios (4 categorías) ---
        for _ in range(5):
            n = rng.integers(20, 500)
            rA = rng.integers(0, 4, size=n)
            # Inyectar correlación para que kappa no sea siempre cero
            rB = np.where(rng.random(n) < 0.85,
                          rA,
                          rng.integers(0, 4, size=n))
            k_our = kappa_w_lineal(rA, rB)
            k_skl = kappa_w_sklearn(rA, rB)
            rel = abs(k_our - k_skl) / max(abs(k_skl), 1e-12)
            ok = rel < TOL_REL_CONCORDANCIA or abs(k_our - k_skl) < 1e-9
            _marcar(f"Kappa-w / muestra n={n}", ok,
                    f"nuestro={k_our:.6e}  sklearn={k_skl:.6e}  rel={rel:.1e}")
            if not ok:
                break

        # --- Concordancia al 100%: acuerdo perfecto ---
        rA = list(range(4)) * 25
        rB = list(rA)
        _marcar("Kappa-w / acuerdo perfecto == 1 (ambas rutas)",
                np.isclose(kappa_w_lineal(rA, rB), 1.0, atol=TOL_ABS) and
                np.isclose(kappa_w_sklearn(rA, rB), 1.0, atol=TOL_ABS))

    # ===================== D. RESUMEN =====================
    n_ok = sum(1 for _, ok in _resultados if ok)
    n_tot = len(_resultados)
    print("\n" + "=" * 65)
    print(f"RESUMEN: {n_ok}/{n_tot} pruebas superadas")
    print("=" * 65)
    return n_ok == n_tot

if __name__ == "__main__":
    todo_ok = correr_pruebas()
    sys.exit(0 if todo_ok else 1)