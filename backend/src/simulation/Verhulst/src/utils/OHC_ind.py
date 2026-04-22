"""
MÓDULO: Conversor de Audiograma a Perfil de Pérdida Auditiva Coclear (OHC_ind)

Este módulo convierte un audiograma clínico (pérdida auditiva en dB por
frecuencia) en los PARÁMETROS INTERNOS del modelo coclear de Verhulst.

Biología:
---------
La pérdida auditiva neurosensorial se debe principalmente al daño de
las células ciliadas externas (OHC). Cuando las OHC se dañan, pierden su
capacidad de amplificar las vibraciones de la membrana basilar, lo que
resulta en umbrales auditivos elevados (pérdida auditiva en dB HL).

Este módulo traduce ese daño clínico (audiograma) en los "polos de Shera"
del modelo, que controlan la ganancia del amplificador coclear en cada
sección. Un polo más alto = menos amplificación = más pérdida auditiva.

Entrada: Audiograma (frecuencias en Hz + pérdida en dB HL)
Salida: StartingPoles.dat (vector de 1001 polos, uno por sección coclear)

- Flexible audiogram frequency lists (any order)
- Robust path handling (spaces ok)
- Outputs Poles/<name>/profile.txt and StartingPoles.dat
"""

import os
import numpy as np
import matplotlib.pyplot as plt

# Try both loaders for .mat files
try:
    from scipy.io import loadmat
except ImportError:
    loadmat = None

try:
    import h5py
except ImportError:
    h5py = None

# ----------------------------- Utils -----------------------------

def load_mat_var(path, candidates):
    """Load a .mat file and return the first matching variable by name."""
    if isinstance(candidates, str):
        candidates = [candidates]
    
    # Try h5py first (for v7.3 files)
    if h5py is not None:
        try:
            with h5py.File(path, 'r') as f:
                keys = list(f.keys())
                for c in candidates:
                    if c in f:
                        data = f[c][:]
                        # If it's a reference to another dataset, dereference it
                        while isinstance(data, np.ndarray) and data.size == 1:
                            ref = data.flat[0]
                            if isinstance(ref, np.ndarray) and ref.dtype == 'object':
                                data = f[ref.flat[0]][:]
                            else:
                                break
                        return data
                if len(keys) == 1:
                    data = f[keys[0]][:]
                    while isinstance(data, np.ndarray) and data.size == 1:
                        ref = data.flat[0]
                        if isinstance(ref, np.ndarray) and ref.dtype == 'object':
                            data = f[ref.flat[0]][:]
                        else:
                            break
                    return data
        except (OSError, ValueError):
            # Not an HDF5 file, fall through to scipy
            pass
    
    # Fallback to scipy's loadmat
    if loadmat is not None:
        M = loadmat(path)
        # Remove meta-keys
        keys = [k for k in M.keys() if not k.startswith('__')]
        for c in candidates:
            if c in M:
                return M[c]
        # If only one non-meta key, return it
        if len(keys) == 1:
            return M[keys[0]]
    
    raise KeyError(f"None of the expected variables {candidates} found in {os.path.basename(path)}")

def ensure_1d(arr):
    arr = np.asarray(arr)
    return np.ravel(arr)

def nearest_index(array, value):
    array = np.asarray(array)
    return int(np.argmin(np.abs(array - value)))

def write_lines(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        for line in lines:
            f.write(line.rstrip() + '\n')

def semilogx_like(ax, x, y, **kwargs):
    ax.plot(x, y, **kwargs)
    ax.set_xscale('log')

# ------------------------ Core computation -----------------------

def ohc_ind(
    name,
    hl_freqs_hz,
    hl_db,
    base_dir=".",
    show_figs=True,
):
    """
    Convierte un audiograma clínico en polos de Shera para el modelo coclear.
    
    Biología del proceso:
    1. Toma las frecuencias y pérdidas del audiograma del paciente.
    2. Interpola la pérdida a lo largo de las 1000 secciones cocleares.
    3. Busca en las trayectorias de polos pre-calculadas (PoleTrajs.mat)
       qué valor de polo produce la pérdida de ganancia equivalente
       a los dB HL del audiograma en cada sección.
    4. Genera un archivo StartingPoles.dat con 1001 valores (1 por sección
       + 1 para el oído medio) que el modelo coclear usará para simular
       el perfil auditivo específico de ese paciente.
    
    Parámetros:
    ----------
    name : str
        Nombre del perfil (carpeta de salida bajo Poles/<name>).
    hl_freqs_hz : list[float]
        Frecuencias del audiograma (Hz), cualquier orden.
    hl_db : list[float]
        Pérdida auditiva (dB HL) por cada frecuencia.
    base_dir : str
        Directorio base con 'mat files', 'Poles/Flat00/StartingPoles.dat', etc.
    show_figs : bool
        Si mostrar gráficos de diagnóstico.
    """

    # --- Paths (handle spaces safely) ---
    mat_dir = os.path.join(base_dir, "mat files")
    poles_flat_dir = os.path.join(base_dir, "Poles", "Flat00")
    out_dir = os.path.join(base_dir, "Poles", name)

    # --- Load model data ---
    # Presente por completitud; no se usa directamente aquí, pero se carga para espejar MATLAB
    _ = load_mat_var(os.path.join(mat_dir, "BWrange.mat"), ["BWrange", "BWrange_Hz"])  # no se usa posteriormente

    # ---- Carga de datos del modelo ----
    # cf: frecuencias características de las 1000 secciones cocleares (Hz)
    cf = ensure_1d(load_mat_var(os.path.join(mat_dir, "cf.mat"), "cf")).astype(float)  # Hz
    # ModelQ: factor de calidad (Q_ERB) normal para cada sección coclear.
    # Representa la agudeza de sintonización frecuencial con OHC sanas.
    ModelQ = ensure_1d(load_mat_var(os.path.join(mat_dir, "ModelQ.mat"), ["ModelQ", "Q"])).astype(float)

    # PoleTrajs.mat: trayectorias de polos pre-calculadas.
    # SMax[polo, sección]: ganancia máxima de la BM para cada combinación
    # de polo y sección coclear. Se usa para determinar qué valor de polo
    # produce la pérdida de ganancia equivalente al audiograma.
    PT = loadmat(os.path.join(mat_dir, "PoleTrajs.mat"))
    BMS = PT.get("BMS", None)
    SMax = PT.get("SMax", None)
    SN   = PT.get("SN", None)
    if SMax is None:
        raise KeyError("Could not find SMax in PoleTrajs.mat. Please check variable names.")
    SMax = np.asarray(SMax)
    if SN is not None:
        SN = np.asarray(SN)

    # Powerlawpar.mat: parámetros a y b de la ley de potencia Q = a * polo^b
    # que relaciona el polo de Shera con el factor de calidad Q_ERB.
    PL = loadmat(os.path.join(mat_dir, "Powerlawpar.mat"))
    a = float(np.ravel(PL.get("a", np.array([np.nan])))[0])
    b = float(np.ravel(PL.get("b", np.array([np.nan])))[0])
    if not np.isfinite(a) or not np.isfinite(b):
        raise KeyError("Powerlawpar.mat must contain scalars 'a' and 'b'.")

    # StartingPoles (Flat00): polos de Shera para audición NORMAL (sin pérdida).
    # Estos son los valores de referencia contra los que se compara la pérdida.
    sp_path = os.path.join(poles_flat_dir, "StartingPoles.dat")
    SP_all = np.loadtxt(sp_path, dtype=float)
    # El primer valor corresponde al oído medio; se remueve para trabajar
    # solo con las 1000 secciones cocleares.
    StartingPoles = ensure_1d(SP_all)[1:]  # length should be 1000
    NHSP = StartingPoles.copy()  # NHSP = Normal Hearing Starting Poles

    # Eje de polos (rango de valores posibles de polos de Shera)
    Poles = np.round(np.arange(0.036, 0.302 + 1e-12, 0.001), 3)  # 0.036:0.001:0.302

    # --- Find nearest NH pole index for each CF section (choose closest above/below) ---
    NHn = np.empty_like(NHSP, dtype=int)
    for k in range(len(NHSP)):
        # first index where Poles > NHSP[k]
        greater = np.where(Poles > NHSP[k])[0]
        if greater.size == 0:
            # All Poles <= NHSP[k]; choose last
            NHn[k] = len(Poles) - 1
            continue
        Hn = greater[0]
        if Hn == 0:
            NHn[k] = 0
        else:
            Ln = Hn - 1
            # pick closer
            if (Poles[Hn] - NHSP[k]) < (NHSP[k] - Poles[Ln]):
                NHn[k] = Hn
            else:
                NHn[k] = Ln

    # --- GainDiff over poles relative to NH starting pole for each CF ---
    n_poles = len(Poles)
    n_cf = len(NHSP)
    if SMax.shape[0] != n_poles or SMax.shape[1] != n_cf:
        raise ValueError(
            f"SMax shape {SMax.shape} does not match expected (nPoles={n_poles}, nCF={n_cf})."
        )
    # ---- Diferencia de ganancia: polos normales vs. cada polo posible ----
    # GainDiff[polo, sección] = cuántos dB de ganancia se pierden al
    # mover el polo desde su valor normal (NH) hasta el valor 'polo'.
    # Biológicamente: cuánta amplificación coclear (de las OHC) se pierde.
    GainDiff = (SMax[NHn, np.arange(n_cf)] - SMax)  # broadcast over rows

    # ---- Audiograma → Pérdida auditiva por sección coclear ----
    # Interpola linealmente la pérdida del audiograma sobre las 1000
    # secciones cocleares, usando el mapa tonotópico de Greenwood.
    hl_freqs_hz = np.asarray(hl_freqs_hz, dtype=float)
    hl_db = np.asarray(hl_db, dtype=float)
    if hl_freqs_hz.shape != hl_db.shape:
        raise ValueError("hl_freqs_hz and hl_db must have the same length.")

    # Map each provided freq to nearest CF index
    probe_idx = [nearest_index(cf, f) for f in hl_freqs_hz]
    # Deduplicate indices by keeping the last provided HL for any duplicate index
    probe_map = {}
    for idx, hl in zip(probe_idx, hl_db):
        probe_map[idx] = float(hl)
    # Ordenar por índice ascendente a lo largo de la cóclea
    probes_sorted = np.array(sorted(probe_map.items()), dtype=object)  # [[idx, hl], ...]
    probes = probes_sorted[:, 0].astype(int)
    hls_at_probes = probes_sorted[:, 1].astype(float)

    # Build HL array over all CF sections via piecewise linear interpolation on index axis
    HL_sections = np.zeros_like(cf, dtype=float)

    # Rellenar antes del primer punto de sondeo
    HL_sections[:probes[0]] = hls_at_probes[0]
    # Segmentos lineales de interpolación
    for i in range(len(probes) - 1):
        i0, i1 = probes[i], probes[i + 1]
        y0, y1 = hls_at_probes[i], hls_at_probes[i + 1]
        if i1 > i0:
            x = np.arange(i0, i1 + 1, dtype=int)
            # Interpolación lineal en el eje de índices cocleares
            HL_sections[i0:i1 + 1] = y0 + (y1 - y0) * (x - i0) / max(1, (i1 - i0))
        else:
            # Should not happen after sorting; safeguard
            HL_sections[i1:i0 + 1] = np.linspace(y1, y0, i0 - i1 + 1)
    # Rellenar después del último punto de sondeo
    HL_sections[probes[-1]:] = hls_at_probes[-1]

    # ---- Buscar polos HI (Hearing Impaired) por cruce de umbral ----
    # Para cada sección coclear, se busca el polo más pequeño cuya
    # pérdida de ganancia (GainDiff) supere la pérdida auditiva (HL)
    # del audiograma interpolado. Ese polo se asigna como el polo HI.
    # Biológicamente: se busca el grado de daño OHC que produce exactamente
    # la pérdida auditiva observada en el audiograma del paciente.
    HISPn = np.empty(n_cf, dtype=int)
    for k in range(n_cf):
        n_found = np.where(GainDiff[:, k] > HL_sections[k])[0]
        if n_found.size == 0:
            HISPn[k] = n_poles - 1  # fallback (last valid index, equivalent to MATLAB's 267)
        else:
            HISPn[k] = int(n_found[0])
    HISP = Poles[HISPn]

    # Se añade un polo extra para la sección del oído medio (sección 0)
    StartingPolesHI = np.concatenate([[HISP[0]], HISP])
    StartingPolesNH = np.concatenate([[NHSP[0]], NHSP])

    # ModelQHI: factor de calidad Q_ERB con pérdida auditiva.
    # Un Q menor = sintonización frecuencial más ancha = peor discriminación.
    ModelQHI = a * np.power(StartingPolesHI, b)

    # ----------------------------- Plots -----------------------------
    # 1) Pole trajectories (if BMS/SN present)
    if BMS is not None and SN is not None:
        fig1, ax1 = plt.subplots()
        # Emulate the MATLAB loop (plot every 100th)
        for n in range(0, 1000, 100):
            # BMS may be cell-like; try to index safely
            try:
                # If BMS is an object array/cell-like
                bn = BMS.ravel()[n]
                y = np.ravel(bn)
                ax1.plot(y)
                ax1.plot(np.ravel(SN[:, n]), np.ravel(SMax[:, n]), 'rs', markersize=3)
            except Exception:
                # Fallback: skip plotting BMS if format unknown
                pass
        ax1.set_xlim(0, 2000)
        ax1.set_title('The Pole Trajectories for Each CF')
        if show_figs:
            plt.show()

    # 2) Audiogram shaping
    fig2, ax2 = plt.subplots()
    semilogx_like(ax2, cf, HL_sections, color='r', linewidth=2, label='Interpolated HL')
    # Scatter the provided audiogram points
    ax2.semilogx(hl_freqs_hz, hl_db, 'bo', linewidth=2, label='Audiogram points')
    ax2.set_xlim(125, 25000)
    ax2.set_ylim(-10, 50)
    ax2.set_yticks(np.arange(-10, 55, 10))
    ax2.invert_yaxis()
    ax2.set_xlabel('Frequency [Hz]')
    ax2.set_ylabel('Hearing Loss [dB]')
    ax2.legend(loc='best', frameon=False)
    if show_figs:
        plt.show()

    # 3) Starting poles & Q
    fig3, (ax3a, ax3b) = plt.subplots(2, 1, figsize=(5, 10))
    ax3a.plot(StartingPoles, 'k-', linewidth=1, label='NHfit')
    ax3a.plot(StartingPolesHI[1:], 'r-', linewidth=2, label='HIfit')  # drop ME to match NH length
    ax3a.set_ylim(0, 0.3)
    ax3a.set_xlabel('cochlear section')
    ax3a.set_ylabel('Starting Pole Value')
    ax3a.legend(loc='upper right', frameon=False)

    # Q vs CF (prepend cf[0] like MATLAB)
    cf_with_me = np.concatenate([[cf[0]], cf])
    ax3b.semilogx(cf_with_me / 1000.0, ModelQ, 'b-', label='NH')
    ax3b.semilogx(cf_with_me / 1000.0, ModelQHI, 'r-', label='HI')
    ax3b.set_xlim(0.04, 23)
    ax3b.set_ylim(0, 20)
    ax3b.set_xlabel('CF [kHz]')
    ax3b.set_ylabel(r'$Q_{ERB}$')
    ax3b.legend(loc='upper left', frameon=False)
    plt.tight_layout()
    if show_figs:
        plt.show()

    # ----------------------------- Save outputs -----------------------------
    os.makedirs(out_dir, exist_ok=True)

    # profile.txt: line1=cf, line2=HL (section-wise)
    prof_path = os.path.join(out_dir, "profile.txt")
    line1 = "\t".join(f"{x:.6f}" for x in cf)
    line2 = "\t".join(f"{x:.6f}" for x in HL_sections)
    write_lines(prof_path, [line1, line2])

    # StartingPoles.dat
    sp_out_path = os.path.join(out_dir, "StartingPoles.dat")
    if name == "Normal":
        np.savetxt(sp_out_path, StartingPolesNH, fmt="%.6E")
    else:
        np.savetxt(sp_out_path, StartingPolesHI, fmt="%.6E")

    return {
        "cf": cf,
        "HL_sections": HL_sections,
        "StartingPolesNH": StartingPolesNH,
        "StartingPolesHI": StartingPolesHI,
        "ModelQ": ModelQ,
        "ModelQHI": ModelQHI,
        "output_dir": out_dir,
    }

# Ejemplo de uso (comentado para evitar ejecución al importar)
# ohc_ind(name='Brent', 
#         hl_freqs_hz=[8000, 6000, 4000, 3000, 2000, 1000, 500, 250, 125], 
#         hl_db=[0, 0, 0, 0, 0, 0, 0, 0, 0])