from __future__ import annotations

import argparse
from pathlib import Path

from gpx_elevation_fft.gpx import load_gpx
from gpx_elevation_fft.plot import DEFAULT_SIZE, plot_fft, stack_images
from gpx_elevation_fft.spectrum import elevation_fft


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plot the FFT of GPX elevation vs time in a Garmin-style chart."
    )
    parser.add_argument("gpx", type=Path, help="Path to a GPX file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="FFT plot path (default: <gpx_stem>_fft.png next to the GPX file)",
    )
    parser.add_argument(
        "--time-domain",
        type=Path,
        help="Optional elevation-vs-time screenshot to stack above the FFT",
    )
    parser.add_argument(
        "--combo-out",
        type=Path,
        help="Stacked image path (default: <gpx_stem>_time_and_fft.png)",
    )
    parser.add_argument(
        "--elapsed",
        action="store_true",
        help="Use elapsed wall time (interpolate across pauses) instead of moving time",
    )
    parser.add_argument(
        "--f-max-mhz",
        type=float,
        default=12.0,
        help="Upper frequency limit of the plot in millihertz (default: 12)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    gpx_path = args.gpx.expanduser().resolve()
    series = load_gpx(gpx_path)
    spectrum = elevation_fft(series, moving_time=not args.elapsed)

    fft_path = args.output or gpx_path.with_name(f"{gpx_path.stem}_fft.png")
    size = DEFAULT_SIZE
    if args.time_domain is not None:
        from PIL import Image

        size = Image.open(args.time_domain).size

    plot_fft(spectrum, fft_path, f_max_hz=args.f_max_mhz / 1000.0, size=size)

    period = spectrum.period_s
    minutes = int(period // 60)
    seconds = int(round(period % 60))
    print(f"points: {len(series.elevation_ft)}")
    print(
        f"elevation: {series.elevation_ft.min():.0f}-{series.elevation_ft.max():.0f} ft"
    )
    print(
        f"peak: {spectrum.peak_amplitude_ft:.0f} ft at {spectrum.peak_hz * 1000:.2f} mHz "
        f"({minutes}:{seconds:02d})"
    )
    print(f"wrote {fft_path}")

    if args.time_domain is not None:
        combo_path = args.combo_out or gpx_path.with_name(f"{gpx_path.stem}_time_and_fft.png")
        stack_images(args.time_domain, fft_path, combo_path)
        print(f"wrote {combo_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
