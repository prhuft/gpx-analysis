from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np

GPX_NS = {"gpx": "http://www.topografix.com/GPX/1/1"}
FT_PER_M = 3.280839895


@dataclass(frozen=True)
class ElevationSeries:
    """Elevation samples from a GPX track.

    `t_elapsed_s` is wall-clock seconds from the first point.
    `t_moving_s` treats each sample as 1 s of moving time (pauses dropped).
    """

    t_elapsed_s: np.ndarray
    t_moving_s: np.ndarray
    elevation_ft: np.ndarray
    name: str | None = None


def load_gpx(path: str | Path) -> ElevationSeries:
    root = ET.parse(path).getroot()
    name_el = root.find(".//gpx:trk/gpx:name", GPX_NS)
    name = name_el.text if name_el is not None else None

    times: list[datetime] = []
    elevations_m: list[float] = []
    for pt in root.findall(".//gpx:trkpt", GPX_NS):
        ele = pt.find("gpx:ele", GPX_NS)
        t = pt.find("gpx:time", GPX_NS)
        if ele is None or t is None or ele.text is None or t.text is None:
            continue
        elevations_m.append(float(ele.text))
        times.append(datetime.fromisoformat(t.text.replace("Z", "+00:00")))

    if not times:
        raise ValueError(f"No timed elevation points in {path}")

    t0 = times[0]
    t_elapsed = np.array([(t - t0).total_seconds() for t in times], dtype=float)
    elevation_ft = np.asarray(elevations_m, dtype=float) * FT_PER_M
    t_moving = np.arange(len(elevation_ft), dtype=float)
    return ElevationSeries(
        t_elapsed_s=t_elapsed,
        t_moving_s=t_moving,
        elevation_ft=elevation_ft,
        name=name,
    )
