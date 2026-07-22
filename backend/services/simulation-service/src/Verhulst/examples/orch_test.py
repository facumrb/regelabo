#!/usr/bin/env python3
"""Orchestrator test: writes staged NPZ partial outputs to a folder
and demonstrates that `PlotOrchestrator` creates PNGs at different times.
"""
import os
import time
import numpy as np
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from utils.plot_orchestrator import PlotOrchestrator, save_partial_output


def make_dummy_output(ch):
    class O:
        pass
    o = O()
    o.cf = np.linspace(250, 8000, 64)
    o.fs_bm = 20000
    o.fs_ihc = 20000
    o.fs_an = 4000
    o.fs_abr = 4000
    t_bm = int(0.1 * o.fs_bm)
    t_an = int(0.1 * o.fs_an)
    o.sheraPt = 0.06 + 0.01 * np.random.randn(t_bm, o.cf.size)
    o.qt_H = np.clip(7 + np.random.randn(t_an, o.cf.size), 0, 14)
    o.wt_H = 30 + np.random.randn(t_an, o.cf.size)
    o.avail_H = np.clip(0.8 + 0.05 * np.random.randn(t_an, o.cf.size), 0, 1)
    o.Imet = 1e-9 * np.random.randn(t_bm, o.cf.size)
    o.Ikf = 1e-9 * np.random.randn(t_bm, o.cf.size)
    o.Iks = 1e-9 * np.random.randn(t_bm, o.cf.size)
    o.ihc = -0.05 + 0.005 * np.random.randn(t_bm, o.cf.size)
    o.cn_exc = np.abs(1000 + 200 * np.random.randn(t_an, o.cf.size))
    o.cn_inh = np.abs(200 * np.random.randn(t_an, o.cf.size))
    o.ic_exc = np.abs(500 + 100 * np.random.randn(t_an, o.cf.size))
    o.ic_inh = np.abs(100 * np.random.randn(t_an, o.cf.size))
    return o


def main():
    outdir = 'orch_test_folder'
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    orch = PlotOrchestrator(outdir)
    orch.start()

    # Write staged outputs with delays to simulate progressive availability
    for i, stage in enumerate(['cochlea', 'ihc', 'an_fibers', 'brainstem']):
        print(f'Writing stage {stage}...')
        o = make_dummy_output(0)
        save_partial_output(0, stage, o, outdir)
        time.sleep(1.5)

    print('All stages written; waiting for orchestrator to finish plots...')
    time.sleep(2.5)
    orch.stop()
    print('Done. Check', os.path.join(outdir, 'plots') if os.path.exists(os.path.join(outdir, 'plots')) else outdir)


if __name__ == '__main__':
    main()
