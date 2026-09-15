"""A very small prototype for forecasting NDVI from GeoTIFF rasters.

This is meant to be easy to read and easy to modify. It keeps the idea simple:

1. Find dated GeoTIFF files.
2. Inspect them.
3. Train a tiny CNN on small image patches.
4. Use the model to create a forecast raster.

Example usage:

    python -m model.model_simple inspect
    python -m model.model_simple train --epochs 3
    python -m model.model_simple predict --checkpoint model/ndvi_prototype.pt

This is a prototype, not a production pipeline.
"""

from __future__ import annotations

import argparse
import logging
import re
from pathlib import Path

import numpy as np

LOGGER = logging.getLogger(__name__)
DATE_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2})")


def _require_packages():
    """Import the required libraries with an easy-to-read error message."""
    try:
        import rasterio
        import torch
        from torch import nn
        from torch.utils.data import DataLoader
    except ImportError as error:
        raise RuntimeError(
           "This prototype needs rasterio and torch. "
           "Install them with: pip install -r model/requirements.txt"
        ) from error
    return rasterio, torch, nn, DataLoader


def find_rasters(data_dir: Path) -> list[Path]:
    """Return GeoTIFF files whose names include a date."""
    rasters = []
    for path in data_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".tif", ".tiff"} and DATE_PATTERN.search(path.name):
           rasters.append(path)

    if not rasters:
        raise FileNotFoundError(f"No dated GeoTIFF files were found in {data_dir}")

    return sorted(rasters, key=lambda path: DATE_PATTERN.search(path.name).group(1))


def inspect_rasters(data_dir: Path) -> list[dict]:
    """Print a simple summary for each raster and check that they match."""
    rasterio, *_ = _require_packages()
    rasters = find_rasters(data_dir)
    infos = []

    for path in rasters:
        with rasterio.open(path) as source:
           values = source.read(1, masked=True)
           valid = values.compressed()
           info = {
               "file": path.name,
               "width": source.width,
               "height": source.height,
               "bands": source.count,
               "dtype": source.dtypes[0],
               "crs": str(source.crs) if source.crs else None,
               "valid_pixels": int(valid.size),
               "min": float(valid.min()) if valid.size else float("nan"),
               "max": float(valid.max()) if valid.size else float("nan"),
               "mean": float(valid.mean()) if valid.size else float("nan"),
           }
           infos.append(info)
           LOGGER.info(
               "%s: %sx%s pixels, bands=%s, dtype=%s, valid=%s, min=%.5g, max=%.5g, mean=%.5g",
               info["file"],
               info["width"],
               info["height"],
               info["bands"],
               info["dtype"],
               info["valid_pixels"],
               info["min"],
               info["max"],
               info["mean"],
           )

    first = infos[0]
    for item in infos[1:]:
        if (
           item["width"],
           item["height"],
           item["bands"],
           item["crs"],
        ) != (
           first["width"],
           first["height"],
           first["bands"],
           first["crs"],
        ):
           raise ValueError("All GeoTIFF files should have the same size and CRS.")

    return infos


def _patch_windows(width: int, height: int, window_size: int):
    """Create a list of square windows for the raster."""
    if width < window_size or height < window_size:
        raise ValueError(
           f"Window size {window_size} is too large for a {width}x{height} raster."
        )

    rows = list(range(0, height - window_size + 1, window_size))
    cols = list(range(0, width - window_size + 1, window_size))

    if rows[-1] != height - window_size:
        rows.append(height - window_size)
    if cols[-1] != width - window_size:
        cols.append(width - window_size)

    for row in rows:
        for col in cols:
           yield row, col


class SimplePatchDataset:
    """Small dataset that stores one patch from each time step."""

    def __init__(self, paths: list[Path], lookback: int, window_size: int):
        rasterio, _, _, _ = _require_packages()
        if len(paths) <= lookback:
           raise ValueError("Not enough GeoTIFF files for the chosen lookback value.")

        with rasterio.open(paths[0]) as source:
           self.width = source.width
           self.height = source.height

        self.paths = paths
        self.lookback = lookback
        self.window_size = window_size
        self.samples = []

        for current_index in range(lookback, len(paths)):
           for row, col in _patch_windows(self.width, self.height, window_size):
               self.samples.append((current_index, row, col))

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int):
        rasterio, torch, *_ = _require_packages()
        current_index, row, col = self.samples[index]
        frames = []

        for file_index in range(current_index - self.lookback, current_index + 1):
           with rasterio.open(self.paths[file_index]) as source:
               window = rasterio.windows.Window(col, row, self.window_size, self.window_size)
               patch = source.read(1, window=window, masked=True).filled(np.nan)
               frames.append(patch)

        data = np.stack(frames[:-1]).astype(np.float32)
        target = frames[-1].astype(np.float32)
        valid = np.isfinite(data).all(axis=0) & np.isfinite(target)

        data = np.nan_to_num(data, nan=0.0)
        target = np.nan_to_num(target, nan=0.0)

        return (
           torch.from_numpy(data),
           torch.from_numpy(target[None]),
           torch.from_numpy(valid),
        )


class SimpleCNN:
    """A very small CNN. Easy to read, easy to change."""

    def __init__(self, lookback: int):
        _, _, nn, _ = _require_packages()
        self.model = nn.Sequential(
           nn.Conv2d(lookback, 8, kernel_size=3, padding=1),
           nn.ReLU(),
           nn.Conv2d(8, 1, kernel_size=1),
        )


def train(data_dir: Path, checkpoint: Path, lookback: int, window_size: int,
          epochs: int, batch_size: int, learning_rate: float) -> None:
    """Train the prototype model."""
    rasterio, torch, _, DataLoader = _require_packages()
    paths = find_rasters(data_dir)

    with rasterio.open(paths[0]) as source:
        if source.count != 1:
           raise ValueError("This prototype expects one-band GeoTIFF files.")

    split = max(lookback + 1, int(len(paths) * 0.8))
    dataset = SimplePatchDataset(paths[:split], lookback, window_size)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    model = SimpleCNN(lookback).model
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    for epoch in range(epochs):
        total_loss = 0.0
        for inputs, targets, valid in loader:
           prediction = model(inputs)
           mask = valid[:, None]
           error = (prediction - targets).pow(2)
           loss = (error * mask).sum() / mask.sum().clamp_min(1)

           optimizer.zero_grad()
           loss.backward()
           optimizer.step()

           total_loss += float(loss)

        LOGGER.info("epoch %s/%s loss=%.6f", epoch + 1, epochs, total_loss / len(loader))

    checkpoint.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"state_dict": model.state_dict(), "lookback": lookback}, checkpoint)
    LOGGER.info("Saved model to %s", checkpoint)


def predict(data_dir: Path, checkpoint: Path, output: Path, window_size: int) -> None:
    """Use the trained model to create a single output raster."""
    rasterio, torch, _, _ = _require_packages()
    paths = find_rasters(data_dir)

    saved = torch.load(checkpoint, map_location="cpu")
    lookback = int(saved["lookback"])
    model = SimpleCNN(lookback).model
    model.load_state_dict(saved["state_dict"])
    model.eval()

    with rasterio.open(paths[-1]) as source:
        profile = source.profile.copy()
        result = np.zeros((source.height, source.width), dtype=np.float32)

        for row, col in _patch_windows(source.width, source.height, window_size):
           frames = []
           for file_index in range(len(paths) - lookback, len(paths)):
               with rasterio.open(paths[file_index]) as frame:
                   window = rasterio.windows.Window(col, row, window_size, window_size)
                   frames.append(frame.read(1, window=window, masked=True).filled(0))

           inputs = torch.from_numpy(np.stack(frames).astype(np.float32))[None]
           with torch.no_grad():
               prediction = model(inputs)[0, 0].numpy()
               result[
                   row:row + window_size,
                   col:col + window_size,
               ] = prediction

        profile.update(dtype="float32", count=1, nodata=None)
        with rasterio.open(output, "w", **profile) as destination:
           destination.write(result, 1)

    LOGGER.info("Forecast written to %s", output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("inspect", "train", "predict"))
    parser.add_argument("--data-dir", type=Path, default=Path("data/GEE Data"))
    parser.add_argument("--checkpoint", type=Path, default=Path("model/ndvi_prototype.pt"))
    parser.add_argument("--output", type=Path, default=Path("data/GEE Data/NDVI_forecast.tif"))
    parser.add_argument("--lookback", type=int, default=3)
    parser.add_argument("--window-size", type=int, default=16)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    if args.window_size < 3:
        parser.error("--window-size must be at least 3")

    if args.command == "inspect":
        inspect_rasters(args.data_dir)
    elif args.command == "train":
        train(
           args.data_dir,
           args.checkpoint,
           args.lookback,
           args.window_size,
           args.epochs,
           args.batch_size,
           args.learning_rate,
        )
    else:
        predict(args.data_dir, args.checkpoint, args.output, args.window_size)


if __name__ == "__main__":
    main()
