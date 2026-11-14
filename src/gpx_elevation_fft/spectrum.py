from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from gpx_elevation_fft.gpx import ElevationSeries


@dataclass(frozen=True)
class Spectrum:
    freq_hz: np.ndarray
    amplitude_ft: np.ndarray
    peak_hz: float
    peak_amplitude_ft: float

    @property
    def period_s(self) -> float:
        if self.peak_hz <= 0:
            return float("nan")
        return 1.0 / self.peak_hz


def elevation_fft(series: ElevationSeries, *, moving_time: bool = True, dt: float = 1.0) -> Spectrum:
    """One-sided amplitude spectrum of linearly detrended elevation."""
    if moving_time:
        t = series.t_moving_s
        elev = series.elevation_ft
    else:
        t = np.arange(0.0, series.t_elapsed_s[-1] + 1e-9, dt)
        elev = np.interp(t, series.t_elapsed_s, series.elevation_ft)

    trend = np.polyval(np.polyfit(t, elev, 1), t)
    residual = elev - trend

    n = residual.size
    freq_hz = np.fft.rfftfreq(n, d=dt)
    amp = np.abs(np.fft.rfft(residual)) * 2.0 / n
    amp[0] *= 0.5

    peak_i = int(np.argmax(amp[1:]) + 1)
    return Spectrum(
        freq_hz=freq_hz,
        amplitude_ft=amp,
        peak_hz=float(freq_hz[peak_i]),
        peak_amplitude_ft=float(amp[peak_i]),
    )
