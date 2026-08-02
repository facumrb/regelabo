"""
=============================================================================
MÓDULO: Visualizaciones Diagnósticas del Modelo Verhulst 2018
=============================================================================
Genera 4 gráficas de variables internas del modelo auditivo para análisis
fonoaudiológico detallado:

  1. Mapa de Calor Coclear (ganancia OHC instantánea)
  2. Panel de Vesículas Sinápticas (dinámica del RRP - HSR)
  3. Corrientes Iónicas de la IHC (Imet, Ikf, Iks + Vm)
  4. Balance Excitación/Inhibición del Tronco Encefálico (CN e IC)

Requisitos:
  - Ejecutar el modelo con storeflag que incluya 'd'
  - matplotlib >= 3.5

Creado para: Proyecto RegelABO (metodología de la investigación)
"""

import numpy as np
import matplotlib.pyplot as plt
import os


# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def _find_cf_index(cf, target_hz):
    """Encuentra el índice del probe point más cercano a la frecuencia objetivo."""
    return np.argmin(np.abs(cf - target_hz))


def _make_time_axis(data, fs):
    """Crea un vector de tiempo en segundos para un array de datos."""
    return np.arange(data.shape[0]) / fs


# =============================================================================
# VISUALIZACIÓN 1: MAPA DE CALOR COCLEAR
# =============================================================================

def plot_cochlear_heatmap(output, fig=None, ax=None, vmin=None, vmax=None):
    """
    Mapa de calor coclear — Ganancia OHC (Polo de Shera) en función
    del tiempo y la frecuencia característica.

    Colores:
      - Verde: polo bajo → OHC amplificando activamente (oído sano)
      - Rojo: polo alto → OHC saturadas / dañadas (pérdida auditiva)

    Parámetros:
    -----------
    output : ModelOutput
        Salida del modelo con storeflag 'd' activo.
    fig, ax : matplotlib Figure y Axes, opcionales
        Si no se proporcionan, se crean automáticamente.
    vmin, vmax : float, opcionales
        Límites del colormap. Por defecto: mínimo de los datos y 0.31 (PoleE).

    Retorna:
    --------
    fig, ax : matplotlib Figure y Axes
    """
    if output.sheraPt is None:
        raise ValueError("sheraPt no disponible. Ejecutar con storeflag que incluya 'd'.")

    if fig is None or ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))

    t = _make_time_axis(output.sheraPt, output.fs_bm)
    cf = output.cf

    # Meshgrid para pcolormesh: tiempo en ms, frecuencia en Hz
    T, CF = np.meshgrid(t * 1000, cf, indexing='ij')

    # Límites del colormap
    if vmin is None:
        vmin = np.percentile(output.sheraPt, 1)
    if vmax is None:
        vmax = 0.31  # PoleE: punto de saturación (máximo polo, mínima ganancia)

    # Colormap: verde (amplificando) → amarillo → rojo (saturado)
    cmap = plt.cm.RdYlGn_r

    im = ax.pcolormesh(T, CF, output.sheraPt,
                       cmap=cmap, vmin=vmin, vmax=vmax,
                       shading='auto', rasterized=True)

    ax.set_yscale('log')
    ax.set_ylabel('Frecuencia Característica (Hz)', fontsize=12)
    ax.set_xlabel('Tiempo (ms)', fontsize=12)
    ax.set_title('Mapa de Calor Coclear — Ganancia OHC (Polo de Shera)',
                 fontsize=14, fontweight='bold')

    # Limitar eje Y a rango audible relevante
    ax.set_ylim([max(cf.min(), 100), min(cf.max(), 16000)])

    # Etiquetas frecuenciales estándar de audiología
    freq_ticks = [250, 500, 1000, 2000, 4000, 8000]
    freq_ticks = [f for f in freq_ticks if cf.min() <= f <= cf.max()]
    ax.set_yticks(freq_ticks)
    ax.set_yticklabels([f'{f}' for f in freq_ticks])

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, label='Polo de Shera (menor = más ganancia)', pad=0.02)

    ax.tick_params(labelsize=10)

    return fig, ax


# =============================================================================
# VISUALIZACIÓN 2: PANEL DE VESÍCULAS SINÁPTICAS
# =============================================================================

def plot_vesicle_panel(output, cf_targets=None, fiber_type='HSR', fig=None, axes=None):
    """
    Panel de vesículas sinápticas — Dinámica del RRP (Ready Releasable Pool)
    para un tipo de fibra (HSR, MSR o LSR) en frecuencias seleccionadas.

    Muestra:
      - qt (azul): vesículas en el RRP (máx 14) — se agotan con cada disparo
      - wt (naranja, escalado): vesículas en el pool de reserva (máx 60)
      - available (verde, eje derecho): fracción de fibras no refractarias

    Parámetros:
    -----------
    output : ModelOutput
        Salida del modelo con storeflag 'd' activo.
    cf_targets : list of float, opcional
        Frecuencias características a graficar (Hz).
        Default: [500, 1000, 4000, 8000]
    fiber_type : str, opcional
        Tipo de fibra: 'HSR', 'MSR' o 'LSR'. Default: 'HSR'
    fig, axes : matplotlib Figure y Axes, opcionales
        Si no se proporcionan, se crean automáticamente.

    Retorna:
    --------
    fig, axes : matplotlib Figure y array de Axes
    """
    fiber_type = fiber_type.upper()
    qt_attr = f"qt_{fiber_type[0]}"
    wt_attr = f"wt_{fiber_type[0]}"
    avail_attr = f"avail_{fiber_type[0]}"

    qt_data = getattr(output, qt_attr, None)
    wt_data = getattr(output, wt_attr, None)
    avail_data = getattr(output, avail_attr, None)

    if qt_data is None:
        raise ValueError(f"{qt_attr} no disponible. Ejecutar con storeflag que incluya 'd'.")

    if cf_targets is None:
        cf_targets = [500, 1000, 4000, 8000]

    n_plots = len(cf_targets)
    if fig is None or axes is None:
        fig, axes = plt.subplots(n_plots, 1, figsize=(12, 3 * n_plots), sharex=True)
    if n_plots == 1:
        axes = [axes]

    t = _make_time_axis(qt_data, output.fs_an)
    cf = output.cf

    for i, target_hz in enumerate(cf_targets):
        idx = _find_cf_index(cf, target_hz)
        actual_cf = cf[idx]
        ax = axes[i]

        # Colores
        color_qt = '#2196F3'   # azul — RRP
        color_wt = '#FF9800'   # naranja — reserva
        color_av = '#4CAF50'   # verde — disponibilidad

        # RRP (qt) — eje izquierdo
        ax.plot(t * 1000, qt_data[:, idx], color=color_qt, linewidth=1.5,
                label='RRP (qt, máx=14)', alpha=0.9)

        # Reserva (wt) escalada al mismo rango que qt para comparación visual
        if wt_data is not None:
            ax.plot(t * 1000, wt_data[:, idx] * (14.0 / 60.0), color=color_wt,
                    linewidth=1.5, label='Reserva (wt, ×14/60)', alpha=0.9, linestyle='--')

        # Línea de capacidad máxima del RRP
        ax.axhline(y=14, color='gray', linestyle=':', alpha=0.5, label='Capacidad RRP')

        ax.set_ylabel('Vesículas', fontsize=10)
        ax.set_ylim([-0.5, 16])
        ax.set_title(f'CF ≈ {actual_cf:.0f} Hz (Fibras {fiber_type})', fontsize=11, fontweight='bold')

        # Fracción disponible (available) — eje derecho
        if avail_data is not None:
            ax2 = ax.twinx()
            ax2.plot(t * 1000, avail_data[:, idx], color=color_av, linewidth=1.5,
                     label='Fibras disponibles', alpha=0.7)
            ax2.set_ylim([0, 1.15])
            ax2.set_ylabel('Fracción disponible', fontsize=10, color=color_av)
            ax2.tick_params(axis='y', labelcolor=color_av)

            # Leyenda combinada
            lines1, labels1 = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=8)
        else:
            ax.legend(loc='upper right', fontsize=8)

    axes[-1].set_xlabel('Tiempo (ms)', fontsize=12)
    fig.suptitle(f'Panel de Vesículas Sinápticas — Dinámica del RRP ({fiber_type})',
                 fontsize=14, fontweight='bold', y=1.02)
    fig.tight_layout()

    return fig, axes


def plot_vesicle_panel_combined(output, cf_targets=None, fig=None, axes=None):
    """
    Panel de vesículas sinápticas combinado — Compara el RRP (qt) de las 3 poblaciones
    de fibras (HSR, MSR, LSR) simultáneamente en las frecuencias seleccionadas.

    Parámetros:
    -----------
    output : ModelOutput
        Salida del modelo con storeflag 'd' activo.
    cf_targets : list of float, opcional
        Frecuencias características a graficar (Hz). Default: [500, 1000, 4000, 8000]
    fig, axes : matplotlib Figure y Axes, opcionales

    Retorna:
    --------
    fig, axes : matplotlib Figure y array de Axes
    """
    if output.qt_H is None:
        raise ValueError("qt_H no disponible. Ejecutar con storeflag que incluya 'd'.")

    if cf_targets is None:
        cf_targets = [500, 1000, 4000, 8000]

    n_plots = len(cf_targets)
    if fig is None or axes is None:
        fig, axes = plt.subplots(n_plots, 1, figsize=(12, 3.2 * n_plots), sharex=True)
    if n_plots == 1:
        axes = [axes]

    t = _make_time_axis(output.qt_H, output.fs_an)
    cf = output.cf

    color_hsr = '#1E88E5'  # Azul para HSR (Alta tasa)
    color_msr = '#FB8C00'  # Naranja para MSR (Media tasa)
    color_lsr = '#E53935'  # Rojo para LSR (Baja tasa / umbral alto)

    for i, target_hz in enumerate(cf_targets):
        idx = _find_cf_index(cf, target_hz)
        actual_cf = cf[idx]
        ax = axes[i]

        # RRP HSR
        ax.plot(t * 1000, output.qt_H[:, idx], color=color_hsr, linewidth=1.8,
                label='HSR (Alta tasa, umbral bajo)', alpha=0.9)

        # RRP MSR (si está disponible)
        if output.qt_M is not None:
            ax.plot(t * 1000, output.qt_M[:, idx], color=color_msr, linewidth=1.8,
                    label='MSR (Tasa media)', alpha=0.9, linestyle='--')

        # RRP LSR (si está disponible)
        if output.qt_L is not None:
            ax.plot(t * 1000, output.qt_L[:, idx], color=color_lsr, linewidth=1.8,
                    label='LSR (Baja tasa, umbral alto)', alpha=0.9, linestyle='-.')

        ax.axhline(y=14, color='gray', linestyle=':', alpha=0.5, label='Capacidad RRP (máx 14)')

        ax.set_ylabel('Vesículas RRP (qt)', fontsize=10)
        ax.set_ylim([-0.5, 16])
        ax.set_title(f'CF ≈ {actual_cf:.0f} Hz — Comparación HSR vs MSR vs LSR',
                     fontsize=11, fontweight='bold')
        ax.legend(loc='upper right', fontsize=8.5)

    axes[-1].set_xlabel('Tiempo (ms)', fontsize=12)
    fig.suptitle('Panel Integrado de Vesículas Sinápticas — Depleción RRP por Tipo de Fibra (HSR / MSR / LSR)',
                 fontsize=14, fontweight='bold', y=1.02)
    fig.tight_layout()

    return fig, axes


# =============================================================================
# VISUALIZACIÓN 3: CORRIENTES DE LA IHC
# =============================================================================

def plot_ihc_currents(output, cf_targets=None, t_max_ms=50, fig=None, axes=None):
    """
    Corrientes iónicas de la célula ciliada interna (IHC).

    Muestra las 3 corrientes como áreas coloreadas con Vm superpuesto:
      - Imet (azul): corriente de transducción MET (despolarizante)
      - Ikf (naranja): corriente K⁺ rápida (repolarizante, τ=0.3ms)
      - Iks (rojo): corriente K⁺ lenta (adaptación, τ=8ms)
      - Vm (línea negra, eje derecho): potencial de membrana

    Parámetros:
    -----------
    output : ModelOutput
        Salida del modelo con storeflag 'd' activo.
    cf_targets : list of float, opcional
        Frecuencias características a graficar (Hz). Default: [1000, 4000]
    t_max_ms : float, opcional
        Ventana temporal a mostrar en milisegundos. Default: 50 ms.
    fig, axes : matplotlib Figure y Axes, opcionales

    Retorna:
    --------
    fig, axes : matplotlib Figure y array de Axes
    """
    if output.Imet is None:
        raise ValueError("Imet no disponible. Ejecutar con storeflag que incluya 'd'.")

    if cf_targets is None:
        cf_targets = [1000, 4000]

    n_plots = len(cf_targets)
    if fig is None or axes is None:
        fig, axes = plt.subplots(n_plots, 1, figsize=(12, 4 * n_plots), sharex=True)
    if n_plots == 1:
        axes = [axes]

    t = _make_time_axis(output.Imet, output.fs_ihc)
    cf = output.cf

    # Limitar a la ventana temporal seleccionada
    max_samples = min(int(t_max_ms * 1e-3 * output.fs_ihc), output.Imet.shape[0])
    t_plot = t[:max_samples] * 1000  # convertir a ms

    for i, target_hz in enumerate(cf_targets):
        idx = _find_cf_index(cf, target_hz)
        actual_cf = cf[idx]
        ax = axes[i]

        # Corrientes en nanoamperes (A → nA) para legibilidad
        Imet_nA = output.Imet[:max_samples, idx] * 1e9
        Ikf_nA = output.Ikf[:max_samples, idx] * 1e9
        Iks_nA = output.Iks[:max_samples, idx] * 1e9

        # Submuestrear para visualización (cada 10 puntos a 100kHz = cada 0.1ms)
        step = max(1, len(t_plot) // 5000)
        t_sub = t_plot[::step]
        Imet_sub = Imet_nA[::step]
        Ikf_sub = Ikf_nA[::step]
        Iks_sub = Iks_nA[::step]

        # Áreas de las corrientes
        ax.fill_between(t_sub, 0, Imet_sub, alpha=0.4, color='#2196F3', label='Imet (MET)')
        ax.fill_between(t_sub, 0, Ikf_sub, alpha=0.4, color='#FF9800', label='Ikf (K⁺ rápido)')
        ax.fill_between(t_sub, 0, Iks_sub, alpha=0.4, color='#f44336', label='Iks (K⁺ lento)')

        ax.set_ylabel('Corriente (nA)', fontsize=10)
        ax.set_title(f'CF ≈ {actual_cf:.0f} Hz', fontsize=11, fontweight='bold')

        # Vm en eje derecho (si está disponible)
        ax2 = ax.twinx()
        if output.ihc is not None:
            Vm_mV = output.ihc[:max_samples, idx] * 1000  # V → mV
            Vm_sub = Vm_mV[::step]
            ax2.plot(t_sub, Vm_sub, color='black', linewidth=1.0, label='Vm', alpha=0.8)
            ax2.set_ylabel('Vm (mV)', fontsize=10)
            ax2.set_ylim([-65, -35])

        # Leyenda combinada
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=8)

    axes[-1].set_xlabel('Tiempo (ms)', fontsize=12)
    fig.suptitle('Corrientes Iónicas de la Célula Ciliada Interna (IHC)',
                 fontsize=14, fontweight='bold', y=1.02)
    fig.tight_layout()

    return fig, axes


# =============================================================================
# VISUALIZACIÓN 4: BALANCE EXCITACIÓN / INHIBICIÓN DEL TRONCO
# =============================================================================

def plot_brainstem_balance(output, cf_targets=None, t_max_ms=50, fig=None, axes=None):
    """
    Balance excitación/inhibición del tronco encefálico.

    Dos filas por cada CF seleccionada:
      - Fila superior: Núcleo Coclear (CN)
      - Fila inferior: Colículo Inferior (IC)

    Cada panel muestra:
      - Área verde: componente excitatoria
      - Área roja (invertida): componente inhibitoria
      - Línea negra: resultado neto (excitación - inhibición)

    Parámetros:
    -----------
    output : ModelOutput
        Salida del modelo con storeflag 'd' activo.
    cf_targets : list of float, opcional
        Frecuencias características a graficar (Hz). Default: [1000, 4000]
    t_max_ms : float, opcional
        Ventana temporal a mostrar en milisegundos. Default: 50 ms.
    fig, axes : matplotlib Figure y 2D array de Axes, opcionales

    Retorna:
    --------
    fig, axes : matplotlib Figure y 2D array de Axes
    """
    if output.cn_exc is None:
        raise ValueError("cn_exc no disponible. Ejecutar con storeflag que incluya 'd'.")

    if cf_targets is None:
        cf_targets = [1000, 4000]

    n_cfs = len(cf_targets)
    if fig is None or axes is None:
        fig, axes = plt.subplots(2, n_cfs, figsize=(6 * n_cfs, 8), sharex=True)
    if n_cfs == 1:
        axes = axes.reshape(2, 1)

    t = _make_time_axis(output.cn_exc, output.fs_abr)
    cf = output.cf

    # Limitar a la ventana temporal seleccionada
    max_samples = min(int(t_max_ms * 1e-3 * output.fs_abr), output.cn_exc.shape[0])
    t_plot = t[:max_samples] * 1000  # ms

    for j, target_hz in enumerate(cf_targets):
        idx = _find_cf_index(cf, target_hz)
        actual_cf = cf[idx]

        # ---- CN (fila 0) ----
        ax_cn = axes[0, j]
        cn_e = output.cn_exc[:max_samples, idx]
        cn_i = output.cn_inh[:max_samples, idx]
        cn_net = cn_e - cn_i

        ax_cn.fill_between(t_plot, 0, cn_e, alpha=0.4, color='#4CAF50', label='Excitación')
        ax_cn.fill_between(t_plot, 0, -cn_i, alpha=0.4, color='#f44336', label='Inhibición')
        ax_cn.plot(t_plot, cn_net, color='black', linewidth=1.2, label='Neto (CN)', alpha=0.9)
        ax_cn.axhline(y=0, color='gray', linewidth=0.5)
        ax_cn.set_title(f'Núcleo Coclear — CF ≈ {actual_cf:.0f} Hz',
                        fontsize=11, fontweight='bold')
        ax_cn.set_ylabel('Actividad (sp/s)', fontsize=10)
        ax_cn.legend(fontsize=8, loc='upper right')

        # ---- IC (fila 1) ----
        ax_ic = axes[1, j]
        ic_e = output.ic_exc[:max_samples, idx]
        ic_i = output.ic_inh[:max_samples, idx]
        ic_net = ic_e - ic_i

        ax_ic.fill_between(t_plot, 0, ic_e, alpha=0.4, color='#4CAF50', label='Excitación')
        ax_ic.fill_between(t_plot, 0, -ic_i, alpha=0.4, color='#f44336', label='Inhibición')
        ax_ic.plot(t_plot, ic_net, color='black', linewidth=1.2, label='Neto (IC)', alpha=0.9)
        ax_ic.axhline(y=0, color='gray', linewidth=0.5)
        ax_ic.set_title(f'Colículo Inferior — CF ≈ {actual_cf:.0f} Hz',
                        fontsize=11, fontweight='bold')
        ax_ic.set_ylabel('Actividad (sp/s)', fontsize=10)
        ax_ic.set_xlabel('Tiempo (ms)', fontsize=12)
        ax_ic.legend(fontsize=8, loc='upper right')

    fig.suptitle('Balance Excitación / Inhibición del Tronco Encefálico',
                 fontsize=14, fontweight='bold', y=1.02)
    fig.tight_layout()

    return fig, axes


# =============================================================================
# FUNCIÓN INTEGRADORA: GENERA LAS 4 VISUALIZACIONES
# =============================================================================

def plot_all_diagnostics(output, save_dir=None, show=True):
    """
    Genera las 4 visualizaciones diagnósticas en figuras separadas.

    Parámetros:
    -----------
    output : ModelOutput
        Salida del modelo con storeflag 'd' activo.
    save_dir : str, opcional
        Directorio donde guardar las figuras como PNG (300 dpi).
        Si no se especifica, no se guardan archivos.
    show : bool
        Si True, muestra las figuras con plt.show() al final.

    Retorna:
    --------
    figs : dict
        Diccionario con las 4 figuras: {'cochlear_heatmap': fig1, ...}
    """
    figs = {}

    # 1. Mapa de calor coclear
    print("  [1/4] Generando mapa de calor coclear...")
    fig1, _ = plot_cochlear_heatmap(output)
    figs['cochlear_heatmap'] = fig1

    # 2. Panel de vesículas sinápticas (HSR, MSR, LSR y Combinado)
    print("  [2/4] Generando panel de vesículas sinápticas (HSR)...")
    fig2_hsr, _ = plot_vesicle_panel(output, fiber_type='HSR')
    figs['vesicle_panel_hsr'] = fig2_hsr

    if hasattr(output, 'qt_M') and output.qt_M is not None:
        print("        Generando panel de vesículas sinápticas (MSR)...")
        fig2_msr, _ = plot_vesicle_panel(output, fiber_type='MSR')
        figs['vesicle_panel_msr'] = fig2_msr

    if hasattr(output, 'qt_L') and output.qt_L is not None:
        print("        Generando panel de vesículas sinápticas (LSR)...")
        fig2_lsr, _ = plot_vesicle_panel(output, fiber_type='LSR')
        figs['vesicle_panel_lsr'] = fig2_lsr

    if hasattr(output, 'qt_H') and output.qt_H is not None:
        print("        Generando panel combinado de vesículas (HSR/MSR/LSR)...")
        fig2_comb, _ = plot_vesicle_panel_combined(output)
        figs['vesicle_panel_combined'] = fig2_comb

    # 3. Corrientes de la IHC
    print("  [3/4] Generando corrientes de la IHC...")
    fig3, _ = plot_ihc_currents(output)
    figs['ihc_currents'] = fig3

    # 4. Balance excitación/inhibición
    print("  [4/4] Generando balance excitación/inhibición...")
    fig4, _ = plot_brainstem_balance(output)
    figs['brainstem_balance'] = fig4

    # Guardar si se especificó directorio
    if save_dir is not None:
        os.makedirs(save_dir, exist_ok=True)
        for name, fig in figs.items():
            filepath = os.path.join(save_dir, f'{name}.png')
            fig.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"  Guardado: {filepath}")

    if show:
        plt.show()

    return figs