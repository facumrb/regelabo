"""
Lightweight plot orchestrator: watches a directory for per-channel
partial-output files (NPZ) produced by the simulation workers and
generates diagnostic figures as soon as the data required for each
visualization becomes available.

Behavior:
- Workers save partial results as `<stage>_<channel_idx>.npz`.
- This module polls the directory, loads new files and calls the
  plotting functions from `diagnostic_plots.py` to create PNGs.

This keeps plot generation asynchronous and allows the user to see
each visualization as soon as possible.
"""
import threading
import time
import os
import numpy as np
from typing import Optional

from .diagnostic_plots import (
    plot_cochlear_heatmap,
    plot_vesicle_panel,
    plot_ihc_currents,
    plot_brainstem_balance,
)


class PlotOrchestrator:
    def __init__(self, watch_dir: str, out_dir: Optional[str] = None, poll_interval: float = 0.5):
        self.watch_dir = os.path.abspath(watch_dir)
        self.out_dir = os.path.abspath(out_dir or os.path.join(self.watch_dir, 'plots'))
        os.makedirs(self.out_dir, exist_ok=True)
        os.makedirs(self.watch_dir, exist_ok=True)
        self.poll_interval = poll_interval
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._seen = set()

    def start(self):
        self._stop_event.clear()
        if not self._thread.is_alive():
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def stop(self):
        self._stop_event.set()
        self._thread.join(timeout=2.0)

    def _run(self):
        while not self._stop_event.is_set():
            try:
                for fname in os.listdir(self.watch_dir):
                    if not fname.endswith('.npz'):
                        continue
                    full = os.path.join(self.watch_dir, fname)
                    if full in self._seen:
                        continue
                    # only try to process files that appear stable (small race window)
                    try:
                        st = os.stat(full)
                    except OSError:
                        continue
                    # load and process
                    try:
                        data = np.load(full, allow_pickle=True)
                    except Exception:
                        # file might be still being written
                        continue
                    # mark as seen as early as possible
                    self._seen.add(full)
                    # find channel and stage from filename convention: <stage>_<ch>.npz
                    base = os.path.basename(full)
                    parts = base[:-4].split('_')
                    if len(parts) < 2:
                        continue
                    stage = '_'.join(parts[:-1])
                    try:
                        ch = int(parts[-1])
                    except Exception:
                        ch = parts[-1]

                    # build a lightweight output object expected by plotting routines
                    class OutObj:
                        pass

                    out = OutObj()
                    # populate any arrays present in the npz
                    for k in data.files:
                        setattr(out, k, data[k])

                    # prefer explicit fs fields if present, otherwise try common names
                    if not hasattr(out, 'fs_bm') and hasattr(out, 'fs'):
                        out.fs_bm = out.fs
                    if not hasattr(out, 'fs_ihc') and hasattr(out, 'fs'):
                        out.fs_ihc = out.fs
                    if not hasattr(out, 'fs_an') and hasattr(out, 'fs'):
                        out.fs_an = out.fs
                    if not hasattr(out, 'fs_abr') and hasattr(out, 'fs'):
                        out.fs_abr = out.fs

                    # create plots based on available fields
                    try:
                        if hasattr(out, 'sheraPt'):
                            fig, ax = plot_cochlear_heatmap(out)
                            fpath = os.path.join(self.out_dir, f'cochlear_heatmap_ch{ch}.png')
                            fig.savefig(fpath, dpi=200, bbox_inches='tight')
                            print(f'[PlotOrch] Saved {fpath}')
                        if hasattr(out, 'qt_H'):
                            fig, axes = plot_vesicle_panel(out)
                            fpath = os.path.join(self.out_dir, f'vesicle_panel_ch{ch}.png')
                            fig.savefig(fpath, dpi=200, bbox_inches='tight')
                            print(f'[PlotOrch] Saved {fpath}')
                        if hasattr(out, 'Imet'):
                            fig, axes = plot_ihc_currents(out)
                            fpath = os.path.join(self.out_dir, f'ihc_currents_ch{ch}.png')
                            fig.savefig(fpath, dpi=200, bbox_inches='tight')
                            print(f'[PlotOrch] Saved {fpath}')
                        if hasattr(out, 'cn_exc'):
                            fig, axes = plot_brainstem_balance(out)
                            fpath = os.path.join(self.out_dir, f'brainstem_balance_ch{ch}.png')
                            fig.savefig(fpath, dpi=200, bbox_inches='tight')
                            print(f'[PlotOrch] Saved {fpath}')
                    except Exception as e:
                        print(f'[PlotOrch] Error generating plots for {full}: {e}')
            except Exception:
                pass
            time.sleep(self.poll_interval)


def save_partial_output(channel_idx: int, stage: str, output, outdir: str):
    """Save selected arrays from a ModelOutput-like object into a compressed NPZ.

    The worker processes can call this function after each stage completes.
    File name convention: `<stage>_<channel_idx>.npz`
    """
    os.makedirs(outdir, exist_ok=True)
    fname = os.path.join(outdir, f"{stage}_{channel_idx}.npz")
    payload = {}
    # include typical fields used by diagnostic plots if present
    fields = [
        'sheraPt', 'cf', 'fs_bm',
        'qt_H', 'wt_H', 'avail_H', 'fs_an',
        'Imet', 'Ikf', 'Iks', 'ihc', 'fs_ihc',
        'cn_exc', 'cn_inh', 'ic_exc', 'ic_inh', 'fs_abr'
    ]
    for f in fields:
        if hasattr(output, f) and getattr(output, f) is not None:
            payload[f] = getattr(output, f)
    if payload:
        try:
            np.savez_compressed(fname, **payload)
        except Exception:
            # fallback to plain save (less robust but avoids crashes)
            np.savez(fname, **payload)
