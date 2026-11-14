# gpx-elevation-fft

Turn a GPX elevation trace into a Garmin-style FFT plot: black background, green filled spectrum, min/max-style header stats.

The pipeline:

1. Read `<trkpt>` elevation and time from a GPX file
2. Build a 1 Hz series on **moving time** (pauses dropped) by default
3. Linearly detrend elevation (feet)
4. Take the one-sided amplitude FFT
5. Plot the low-frequency spectrum and optionally stack it under a time-domain screenshot

## Setup

```bash
uv sync
```

Or:

```bash
pip install -e .
```

## Usage

```bash
gpx-elevation-fft path/to/activity.gpx
```

Writes `activity_fft.png` next to the GPX file.

Stack the FFT under an existing elevation-vs-time screenshot:

```bash
gpx-elevation-fft path/to/activity.gpx --time-domain screenshot.jpg --combo-out stacked.png
```

Use elapsed wall time instead of moving time:

```bash
gpx-elevation-fft path/to/activity.gpx --elapsed
```

## Notes

- Elevation is converted from meters to feet (`× 3.280839895`).
- FFT amplitudes use the single-sided `2/N` scaling so a sinusoid of amplitude `A` peaks near `A`.
- The default x-axis runs from 0 to 12 mHz, which covers the lap fundamental and the first few harmonics for typical ride loops.
