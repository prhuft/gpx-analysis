from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from gpx_elevation_fft.spectrum import Spectrum

GREEN = "#2EE56A"
GREEN_LINE = "#7CFF9A"
LABEL = "#FFFFFF"
MUTED = "#9AA0A6"
BG = "#000000"

DEFAULT_SIZE = (1080, 690)
DEFAULT_DPI = 100


def _period_label(period_s: float) -> str:
    minutes = int(period_s // 60)
    seconds = int(round(period_s % 60))
    if seconds == 60:
        minutes += 1
        seconds = 0
    return f"{minutes}:{seconds:02d}"


def plot_fft(
    spectrum: Spectrum,
    out_path: str | Path,
    *,
    f_max_hz: float = 0.012,
    size: tuple[int, int] = DEFAULT_SIZE,
    dpi: int = DEFAULT_DPI,
) -> Path:
    """Write a Garmin-style filled FFT plot. Aspect ratio matches `size`."""
    out_path = Path(out_path)
    width, height = size
    mask = spectrum.freq_hz <= f_max_hz
    f_mhz = spectrum.freq_hz[mask] * 1000.0
    amp = spectrum.amplitude_ft[mask]

    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Segoe UI", "Arial", "DejaVu Sans"],
            "text.color": LABEL,
            "axes.facecolor": BG,
            "figure.facecolor": BG,
            "savefig.facecolor": BG,
            "axes.edgecolor": BG,
            "axes.labelcolor": MUTED,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "axes.linewidth": 0,
        }
    )

    fig, ax = plt.subplots(figsize=(width / dpi, height / dpi), dpi=dpi)
    fig.subplots_adjust(left=0.105, right=0.965, top=0.76, bottom=0.175)

    ax.fill_between(f_mhz, amp, 0, color=GREEN, linewidth=0, zorder=2)
    ax.plot(f_mhz, amp, color=GREEN_LINE, linewidth=1.4, solid_capstyle="round", zorder=3)

    ymax = max(75.0, float(np.max(amp)) * 1.2)
    ax.set_xlim(0, f_max_hz * 1000.0)
    ax.set_ylim(0, ymax)

    yticks = np.linspace(0, ymax, 6)
    ax.set_yticks(yticks)
    ax.set_yticklabels([f"{v:.0f}" for v in yticks], fontsize=14)
    ax.tick_params(axis="y", length=0, pad=10)

    xticks = np.linspace(0, f_max_hz * 1000.0, 6)
    ax.set_xticks(xticks)
    ax.set_xticklabels(
        [f"{v:.0f}" if float(v).is_integer() else f"{v:.1f}" for v in xticks],
        fontsize=14,
    )
    ax.tick_params(axis="x", length=0, pad=12)

    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(False)
    ax.set_xlabel("Frequency (mHz)", fontsize=13, color=MUTED, labelpad=12)

    fig.text(
        0.055,
        0.915,
        f"{spectrum.peak_amplitude_ft:.0f} ft",
        fontsize=32,
        color=LABEL,
        ha="left",
        va="center",
    )
    fig.text(0.055, 0.845, "Peak amplitude", fontsize=13, color=MUTED, ha="left", va="center")
    fig.text(
        0.52,
        0.915,
        f"{spectrum.peak_hz * 1000:.2f} mHz",
        fontsize=32,
        color=LABEL,
        ha="left",
        va="center",
    )
    fig.text(
        0.52,
        0.845,
        f"Peak frequency  •  {_period_label(spectrum.period_s)}",
        fontsize=13,
        color=MUTED,
        ha="left",
        va="center",
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=dpi, facecolor=BG)
    plt.close(fig)
    return out_path


def stack_images(top_path: str | Path, bottom_path: str | Path, out_path: str | Path) -> Path:
    """Place `bottom_path` under `top_path`, matching the top image size."""
    top = Image.open(top_path).convert("RGB")
    bottom = Image.open(bottom_path).convert("RGB")
    if bottom.size != top.size:
        bottom = bottom.resize(top.size, Image.Resampling.LANCZOS)

    combo = Image.new("RGB", (top.width, top.height * 2), (0, 0, 0))
    combo.paste(top, (0, 0))
    combo.paste(bottom, (0, top.height))
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    combo.save(out_path)
    return out_path
