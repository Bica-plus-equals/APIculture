"""Deterministic placeholder for the future CNN and clustering pipeline.

Replace the body of ``run_placeholder_inference`` with the real model later.
Keeping the returned keys unchanged means the API and frontend will continue to
work while the scientific implementation evolves.
"""

# from __future__ import annotations

# from datetime import date, datetime, timezone
# from math import cos, pi, sin


# FARM_SOUTH = 45.010
# FARM_WEST = 28.000
# FARM_NORTH = 45.030
# FARM_EAST = 28.035


# def _bounded(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
#     return max(minimum, min(maximum, value))


# def _placeholder_raster(selected_date: date, rows: int = 5, columns: int = 6) -> list[dict]:
#     """Return a small JSON grid that visually stands in for a future GeoTIFF."""

#     day_phase = 2 * pi * selected_date.timetuple().tm_yday / 365.25
#     latitude_step = (FARM_NORTH - FARM_SOUTH) / rows
#     longitude_step = (FARM_EAST - FARM_WEST) / columns
#     cells: list[dict] = []

#     for row in range(rows):
#         for column in range(columns):
#             spatial_pattern = 0.12 * sin((row + 1) * 1.4) + 0.10 * cos((column + 1) * 1.1)
#             seasonal_pattern = 0.52 + 0.22 * sin(day_phase - 0.8)
#             value = round(_bounded(seasonal_pattern + spatial_pattern), 3)
#             cells.append(
#                 {
#                     "south": round(FARM_SOUTH + row * latitude_step, 6),
#                     "west": round(FARM_WEST + column * longitude_step, 6),
#                     "north": round(FARM_SOUTH + (row + 1) * latitude_step, 6),
#                     "east": round(FARM_WEST + (column + 1) * longitude_step, 6),
#                     "value": value,
#                 }
#             )

#     return cells


