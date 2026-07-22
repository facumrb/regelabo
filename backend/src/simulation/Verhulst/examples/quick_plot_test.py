#!/usr/bin/env python3
"""Quick test to generate diagnostic plots using synthetic data.

Run from the examples directory. This avoids running the full cochlear
simulation but verifies the plotting functions and file saving.
"""
import os
import sys
import numpy as np

# Ensure src is on path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from utils.diagnostic_plots import plot_all_diagnostics


class OutObj:
    pass


def make_synthetic_output():
    out = OutObj()
    # frequencies (CF) and sampling rates
    out.cf = np.linspace(100, 8000, 128)
    out.fs_bm = 20000
    out.fs_ihc = 20000
    out.fs_an = 4000
    out.fs_abr = 4000

    t_bm = int(0.4 * out.fs_bm)  # 0.4 s
    t_an = int(0.4 * out.fs_an)

    # she ra poles: time x sections
    out.sheraPt = 0.06 + 0.02 * np.sin(np.linspace(0, 20 * np.pi, t_bm))[:, None] * (
        np.linspace(1.0, 0.5, out.cf.size)[None, :]
    )

    # vesicle panel arrays (time_an x sections)
    out.qt_H = np.clip(10 + 2 * np.sin(np.linspace(0, 30 * np.pi, t_an))[:, None] * np.ones((1, out.cf.size)), 0, 14)
    out.wt_H = 30 + 5 * np.cos(np.linspace(0, 10 * np.pi, t_an))[:, None] * np.ones((1, out.cf.size))
    out.avail_H = np.clip(0.8 + 0.1 * np.sin(np.linspace(0, 8 * np.pi, t_an))[:, None] * np.ones((1, out.cf.size)), 0, 1)

    out.qt_M = np.clip(12 + 1.5 * np.sin(np.linspace(0, 20 * np.pi, t_an))[:, None] * np.ones((1, out.cf.size)), 0, 14)
    out.wt_M = 40 + 4 * np.cos(np.linspace(0, 8 * np.pi, t_an))[:, None] * np.ones((1, out.cf.size))
    out.avail_M = np.clip(0.85 + 0.08 * np.sin(np.linspace(0, 6 * np.pi, t_an))[:, None] * np.ones((1, out.cf.size)), 0, 1)

    out.qt_L = np.clip(13.5 + 0.8 * np.sin(np.linspace(0, 10 * np.pi, t_an))[:, None] * np.ones((1, out.cf.size)), 0, 14)
    out.wt_L = 50 + 3 * np.cos(np.linspace(0, 6 * np.pi, t_an))[:, None] * np.ones((1, out.cf.size))
    out.avail_L = np.clip(0.9 + 0.05 * np.sin(np.linspace(0, 4 * np.pi, t_an))[:, None] * np.ones((1, out.cf.size)), 0, 1)

    # IHC currents (time_bm x sections) - create smaller amplitude signals
    out.Imet = 1e-9 * (0.2 * np.sin(np.linspace(0, 50 * np.pi, t_bm))[:, None] * np.ones((1, out.cf.size)))
    out.Ikf = 1e-9 * (0.05 * np.cos(np.linspace(0, 40 * np.pi, t_bm))[:, None] * np.ones((1, out.cf.size)))
    out.Iks = 1e-9 * (0.02 * np.sin(np.linspace(0, 20 * np.pi, t_bm))[:, None] * np.ones((1, out.cf.size)))
    out.ihc = -0.05 + 0.005 * np.sin(np.linspace(0, 50 * np.pi, t_bm))[:, None] * np.ones((1, out.cf.size))

    # brainstem excitation/inhibition (time_an x sections)
    out.cn_exc = 2000 + 500 * np.abs(np.sin(np.linspace(0, 10 * np.pi, t_an)))[:, None] * np.ones((1, out.cf.size))
    out.cn_inh = 500 * np.abs(np.cos(np.linspace(0, 8 * np.pi, t_an)))[:, None] * np.ones((1, out.cf.size))
    out.ic_exc = 1000 + 300 * np.abs(np.sin(np.linspace(0, 12 * np.pi, t_an)))[:, None] * np.ones((1, out.cf.size))
    out.ic_inh = 300 * np.abs(np.cos(np.linspace(0, 6 * np.pi, t_an)))[:, None] * np.ones((1, out.cf.size))

    return out


if __name__ == '__main__':
    out = make_synthetic_output()
    save_dir = 'test_plots'
    if os.path.exists(save_dir):
        # clean old results
        for f in os.listdir(save_dir):
            try:
                os.remove(os.path.join(save_dir, f))
            except Exception:
                pass
    print('Generating diagnostic plots into', save_dir)
    figs = plot_all_diagnostics(out, save_dir=save_dir, show=False)
    print('Saved files:')
    for f in sorted(os.listdir(save_dir)):
        print(' -', f)
