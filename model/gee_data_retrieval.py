#!/usr/bin/env python3
"""Retrieve model-ready phenology data from Google Earth Engine.

The script supports two commands:

1. ``training`` creates a sampled CSV containing model features and weak
   flowering labels for several dates.
2. ``raster`` downloads a multiband GeoTIFF containing the same model features
   for one target date.

The flowering label is only a spectral proxy. It is useful for prototyping,
especially for conspicuous yellow crops, but it is not field-verified nectar or
flowering ground truth.
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable, Sequence

import ee
import requests


LOGGER = logging.getLogger("phenology_retrieval")

# Sentinel-2 input bands and their clearer model-facing names.
S2_BANDS = ["B2", "B3", "B4", "B5", "B8", "B8A", "B11"]
REFLECTANCE_FEATURES = [
    "blue", "green", "red", "rededge1", "nir", "nir_narrow", "swir1"
]
SPECTRAL_INDICES = ["ndvi", "evi", "ndre", "ndmi", "ndyi"]
DELTA_FEATURES = [f"d_{name}" for name in SPECTRAL_INDICES]
CLIMATE_FEATURES = [
    "gdd", "tmean_1d", "tmean_7d", "precip_1d", "precip_7d",
    "precip_30d", "solar_7d", "wind_1d",
]
CONTEXT_FEATURES = [
    "crop_prob", "tree_prob", "grass_prob", "elevation", "slope",
    "doy_sin", "doy_cos",
]
FEATURE_BANDS = (
    REFLECTANCE_FEATURES
    + SPECTRAL_INDICES
    + DELTA_FEATURES
    + CLIMATE_FEATURES
    + CONTEXT_FEATURES
)

LABEL_BAND = "label"
NODATA = -9999.0


@dataclass(frozen=True)
class RetrievalConfig:
    """Settings used by both training and raster retrieval."""

    recent_window_days: int = 20
    previous_window_days: int = 20
    cloud_score_threshold: float = 0.60
    base_temperature_c: float = 5.0
    scale_m: int = 20
    # Thresholds used only to create the prototype label.
    bloom_ndyi_threshold: float = 0.05
    minimum_ndvi: float = 0.25
    greening_delta_threshold: float = 0.04
    future_label_window_days: int = 10


def initialise_earth_engine(project: str | None, authenticate: bool = False) -> None:
    """Connect to Earth Engine, optionally starting interactive authentication."""

    try:
        ee.Initialize(project=project)
    except Exception as exc:
        if not authenticate:
            raise RuntimeError(
                "Earth Engine is not authenticated. Run `earthengine authenticate` "
                "once, or repeat this command with --authenticate."
            ) from exc

        ee.Authenticate()
        ee.Initialize(project=project)


def parse_iso_date(value: str) -> date:
    """Convert a YYYY-MM-DD command-line value into a Python date."""

    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Dates must use YYYY-MM-DD.") from exc


def parse_bbox(value: str) -> tuple[float, float, float, float]:
    """Parse and validate west,south,east,north coordinates."""

    try:
        west, south, east, north = [float(part) for part in value.split(",")]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "Bounding box must be west,south,east,north."
        ) from exc

    valid = -180 <= west < east <= 180 and -90 <= south < north <= 90
    if not valid:
        raise argparse.ArgumentTypeError("Bounding-box coordinates are invalid.")

    return west, south, east, north


def geometry_from_bbox(bbox: Sequence[float]) -> ee.Geometry:
    """Turn a bounding box into an Earth Engine rectangle."""

    return ee.Geometry.Rectangle(list(bbox), proj="EPSG:4326", geodesic=False)


def utm_crs_for_bbox(bbox: Sequence[float]) -> str:
    """Choose a metre-based UTM coordinate system for the AOI centre."""

    west, south, east, north = bbox
    longitude = (west + east) / 2
    latitude = (south + north) / 2
    zone = math.floor((longitude + 180) / 6) + 1
    epsg = 32600 + zone if latitude >= 0 else 32700 + zone
    return f"EPSG:{epsg}"


def iter_dates(start: date, end: date, step_days: int) -> Iterable[date]:
    """Yield dates from start to end, including both endpoints when reached."""

    if end < start:
        raise ValueError("end date must not precede start date")
    if step_days < 1:
        raise ValueError("step_days must be positive")

    current = start
    while current <= end:
        yield current
        current += timedelta(days=step_days)


def _add_spectral_indices(image: ee.Image) -> ee.Image:
    """Rename Sentinel-2 bands and calculate five vegetation indices."""

    blue = image.select("B2")
    green = image.select("B3")
    red = image.select("B4")
    rededge = image.select("B5")
    nir = image.select("B8")
    nir_narrow = image.select("B8A")
    swir = image.select("B11")

    def normalised_difference(
        first: ee.Image,
        second: ee.Image,
        name: str,
    ) -> ee.Image:
        return (
            first.subtract(second)
            .divide(first.add(second).max(1e-6))
            .clamp(-1, 1)
            .rename(name)
        )

    ndvi = normalised_difference(nir, red, "ndvi")
    ndre = normalised_difference(nir_narrow, rededge, "ndre")
    ndmi = normalised_difference(nir, swir, "ndmi")
    ndyi = normalised_difference(green, blue, "ndyi")
    evi = (
        nir.subtract(red)
        .multiply(2.5)
        .divide(nir.add(red.multiply(6)).subtract(blue.multiply(7.5)).add(1))
        .clamp(-2, 2)
        .rename("evi")
    )

    reflectance = image.rename(REFLECTANCE_FEATURES)
    indices = ee.Image.cat(ndvi, evi, ndre, ndmi, ndyi)
    return reflectance.addBands(indices)


def _sentinel_composite(
    start: ee.Date,
    end: ee.Date,
    aoi: ee.Geometry,
    cloud_score_threshold: float,
) -> ee.Image:
    """Create a cloud-masked median Sentinel-2 composite for one time window."""

    sentinel = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(aoi)
        .filterDate(start, end)
        .filter(ee.Filter.lte("CLOUDY_PIXEL_PERCENTAGE", 80))
    )
    cloud_scores = ee.ImageCollection("GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED")
    linked = sentinel.linkCollection(cloud_scores, ["cs_cdf"])

    def mask_and_scale(image: ee.Image) -> ee.Image:
        clear_pixels = image.select("cs_cdf").gte(cloud_score_threshold)
        return image.select(S2_BANDS).multiply(0.0001).updateMask(clear_pixels)

    # This masked image keeps the expected bands even when no clear scene exists.
    empty_image = (
        ee.Image.constant([0.0] * len(S2_BANDS))
        .rename(S2_BANDS)
        .updateMask(ee.Image.constant(0))
    )
    collection = linked.map(mask_and_scale).merge(
        ee.ImageCollection.fromImages([empty_image])
    )
    return _add_spectral_indices(collection.median()).clip(aoi)


def _era5_daily_collection(start: ee.Date, end: ee.Date) -> ee.ImageCollection:
    """Load ERA5-Land daily weather and convert it into convenient units."""

    source = ee.ImageCollection("ECMWF/ERA5_LAND/DAILY_AGGR").filterDate(start, end)

    def convert(image: ee.Image) -> ee.Image:
        temperature = image.select("temperature_2m").subtract(273.15).rename("tmean")
        precipitation = (
            image.select("total_precipitation_sum").multiply(1000).rename("precip")
        )
        solar = (
            image.select("surface_solar_radiation_downwards_sum")
            .divide(86400)
            .rename("solar")
        )
        wind = (
            image.select("u_component_of_wind_10m")
            .pow(2)
            .add(image.select("v_component_of_wind_10m").pow(2))
            .sqrt()
            .rename("wind")
        )
        return ee.Image.cat(temperature, precipitation, solar, wind).copyProperties(
            image, ["system:time_start"]
        )

    return source.map(convert)


def _climate_features(target: date, config: RetrievalConfig) -> ee.Image:
    """Calculate GDD and recent temperature, rain, solar, and wind features."""

    target_ee = ee.Date(target.isoformat())
    end = target_ee.advance(1, "day")
    year_start = ee.Date.fromYMD(target.year, 1, 1)

    # One collection covers the GDD period and the 30-day rolling window.
    history = _era5_daily_collection(year_start.advance(-29, "day"), end)
    current_year = history.filterDate(year_start, end)
    daily = history.filterDate(target_ee, end)
    last_7 = history.filterDate(target_ee.advance(-6, "day"), end)
    last_30 = history.filterDate(target_ee.advance(-29, "day"), end)

    def degree_days(image: ee.Image) -> ee.Image:
        return image.select("tmean").subtract(config.base_temperature_c).max(0)

    gdd = current_year.map(degree_days).sum().rename("gdd")
    return ee.Image.cat(
        gdd,
        daily.select("tmean").mean().rename("tmean_1d"),
        last_7.select("tmean").mean().rename("tmean_7d"),
        daily.select("precip").sum().rename("precip_1d"),
        last_7.select("precip").sum().rename("precip_7d"),
        last_30.select("precip").sum().rename("precip_30d"),
        last_7.select("solar").mean().rename("solar_7d"),
        daily.select("wind").mean().rename("wind_1d"),
    )


def _context_features(target: date, aoi: ee.Geometry) -> ee.Image:
    """Add land-cover probabilities, terrain, and seasonal position."""

    target_ee = ee.Date(target.isoformat())
    dynamic_world = (
        ee.ImageCollection("GOOGLE/DYNAMICWORLD/V1")
        .filterBounds(aoi)
        .filterDate(target_ee.advance(-45, "day"), target_ee.advance(1, "day"))
        .select(["crops", "trees", "grass"])
    )
    empty_cover = (
        ee.Image.constant([0.0, 0.0, 0.0])
        .rename(["crops", "trees", "grass"])
        .updateMask(ee.Image.constant(0))
    )
    cover = dynamic_world.merge(
        ee.ImageCollection.fromImages([empty_cover])
    ).median()
    cover = cover.rename(["crop_prob", "tree_prob", "grass_prob"])

    elevation = ee.Image("USGS/SRTMGL1_003").select("elevation")
    slope = ee.Terrain.slope(elevation).rename("slope")

    day_of_year = target.timetuple().tm_yday
    angle = 2 * math.pi * day_of_year / 365.25
    season = ee.Image.constant([math.sin(angle), math.cos(angle)]).rename(
        ["doy_sin", "doy_cos"]
    )

    return ee.Image.cat(cover, elevation, slope, season).clip(aoi)


def build_feature_image(
    target: date,
    aoi: ee.Geometry,
    config: RetrievalConfig,
) -> ee.Image:
    """Build the complete, ordered model-input image for one date."""

    target_ee = ee.Date(target.isoformat())
    recent_start = target_ee.advance(-config.recent_window_days + 1, "day")
    previous_start = recent_start.advance(-config.previous_window_days, "day")

    recent = _sentinel_composite(
        recent_start,
        target_ee.advance(1, "day"),
        aoi,
        config.cloud_score_threshold,
    )
    previous = _sentinel_composite(
        previous_start,
        recent_start,
        aoi,
        config.cloud_score_threshold,
    )
    delta = (
        recent.select(SPECTRAL_INDICES)
        .subtract(previous.select(SPECTRAL_INDICES))
        .rename(DELTA_FEATURES)
    )

    image = ee.Image.cat(
        recent.select(REFLECTANCE_FEATURES + SPECTRAL_INDICES),
        delta,
        _climate_features(target, config),
        _context_features(target, aoi),
    )
    return (
        image.select(FEATURE_BANDS)
        .toFloat()
        .clip(aoi)
        .set("target_date", target.isoformat())
        .set("climate_source", "era5")
    )


def build_proxy_label(
    target: date,
    aoi: ee.Geometry,
    config: RetrievalConfig,
) -> ee.Image:
    """Create prototype classes: 0=other, 1=approaching, 2=flowering."""

    target_ee = ee.Date(target.isoformat())
    centred = _sentinel_composite(
        target_ee.advance(-4, "day"),
        target_ee.advance(5, "day"),
        aoi,
        config.cloud_score_threshold,
    )
    future = _sentinel_composite(
        target_ee.advance(5, "day"),
        target_ee.advance(5 + config.future_label_window_days, "day"),
        aoi,
        config.cloud_score_threshold,
    )

    land_cover = _context_features(target, aoi)
    vegetation = (
        land_cover.select(["crop_prob", "tree_prob", "grass_prob"])
        .reduce(ee.Reducer.max())
        .gte(0.35)
    )
    viable = centred.select("ndvi").gte(config.minimum_ndvi).And(vegetation)
    flowering = centred.select("ndyi").gte(config.bloom_ndyi_threshold).And(viable)
    future_flowering = future.select("ndyi").gte(config.bloom_ndyi_threshold)
    rapid_greening = future.select("ndvi").subtract(centred.select("ndvi")).gte(
        config.greening_delta_threshold
    )
    approaching = viable.And(flowering.Not()).And(future_flowering.Or(rapid_greening))

    label = ee.Image.constant(0).where(approaching, 1).where(flowering, 2)
    return label.rename(LABEL_BAND).toByte().clip(aoi)


def sample_training_date(
    target: date,
    aoi: ee.Geometry,
    config: RetrievalConfig,
    samples_per_class: int,
    seed: int,
) -> ee.FeatureCollection:
    """Sample an equal target number of pixels from each proxy class."""

    sample_image = build_feature_image(target, aoi, config).addBands(
        ee.Image.cat(
            build_proxy_label(target, aoi, config),
            ee.Image.pixelLonLat().rename(["longitude", "latitude"]),
        )
    )
    sampled = sample_image.stratifiedSample(
        numPoints=samples_per_class,
        classBand=LABEL_BAND,
        region=aoi,
        scale=config.scale_m,
        seed=seed,
        geometries=False,
        tileScale=4,
        dropNulls=True,
    )

    metadata = {
        "date": target.isoformat(),
        "year": target.year,
        "day_of_year": target.timetuple().tm_yday,
        "label_source": "proxy_yellow",
        "climate_source": "era5",
    }
    return sampled.map(lambda feature: feature.set(metadata))


def _download_url(url: str, output_path: Path, timeout: int) -> None:
    """Stream a URL to disk without loading the whole response into memory."""

    with requests.get(url, stream=True, timeout=timeout) as response:
        response.raise_for_status()
        with output_path.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)


def download_feature_collection_csv(
    collection: ee.FeatureCollection,
    output_path: Path,
    selectors: Sequence[str],
) -> None:
    """Download selected FeatureCollection columns as a CSV file."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    url = collection.getDownloadURL(filetype="CSV", selectors=list(selectors))
    LOGGER.info("Downloading sampled training table to %s", output_path)
    _download_url(url, output_path, timeout=600)


def download_image_geotiff(
    image: ee.Image,
    aoi: ee.Geometry,
    output_path: Path,
    scale_m: int,
    crs: str,
) -> None:
    """Download a small or medium AOI as one multiband GeoTIFF."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    url = image.unmask(NODATA).getDownloadURL(
        {
            "region": aoi,
            "scale": scale_m,
            "crs": crs,
            "format": "GEO_TIFF",
            "filePerBand": False,
        }
    )

    with tempfile.TemporaryDirectory(prefix="phenology_ee_") as temp_directory:
        payload = Path(temp_directory) / "earth_engine_download"
        LOGGER.info("Downloading feature raster to %s", output_path)
        _download_url(url, payload, timeout=1200)

        if not zipfile.is_zipfile(payload):
            shutil.move(str(payload), output_path)
            return

        with zipfile.ZipFile(payload) as archive:
            tiff_files = [
                name for name in archive.namelist() if name.lower().endswith(".tif")
            ]
            if len(tiff_files) != 1:
                raise RuntimeError(
                    "Expected one GeoTIFF in the Earth Engine download, "
                    f"found {len(tiff_files)}."
                )
            with archive.open(tiff_files[0]) as source, output_path.open("wb") as target:
                shutil.copyfileobj(source, target)


def retrieve_feature_raster(
    target: date,
    bbox: Sequence[float],
    output_path: Path,
    config: RetrievalConfig,
    crs: str | None = None,
) -> Path:
    """Build, download, and describe a one-date inference raster."""

    aoi = geometry_from_bbox(bbox)
    chosen_crs = crs or utm_crs_for_bbox(bbox)
    image = build_feature_image(target, aoi, config)
    download_image_geotiff(image, aoi, output_path, config.scale_m, chosen_crs)

    metadata_path = output_path.with_suffix(output_path.suffix + ".bands.json")
    metadata_path.write_text(
        json.dumps(
            {
                "bands": FEATURE_BANDS,
                "target_date": target.isoformat(),
                "bbox": list(bbox),
                "crs": chosen_crs,
                "scale_m": config.scale_m,
                "nodata": NODATA,
                "climate_source": "era5",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return output_path


def build_parser() -> argparse.ArgumentParser:
    """Define the training and raster command-line interfaces."""

    shared = argparse.ArgumentParser(add_help=False)
    shared.add_argument(
        "--bbox", required=True, type=parse_bbox, help="west,south,east,north"
    )
    shared.add_argument("--project", help="Google Cloud project used by Earth Engine")
    shared.add_argument(
        "--authenticate",
        action="store_true",
        help="run interactive Earth Engine authentication if needed",
    )
    shared.add_argument(
        "--scale", type=int, default=20, help="output/sample scale in metres"
    )
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    training = commands.add_parser(
        "training", parents=[shared], help="download a sampled training CSV"
    )
    training.add_argument("--start-date", required=True, type=parse_iso_date)
    training.add_argument("--end-date", required=True, type=parse_iso_date)
    training.add_argument("--step-days", type=int, default=7)
    training.add_argument("--samples-per-class", type=int, default=500)
    training.add_argument("--seed", type=int, default=42)
    training.add_argument("--output", required=True, type=Path)

    raster = commands.add_parser(
        "raster", parents=[shared], help="download a feature GeoTIFF for one date"
    )
    raster.add_argument("--date", required=True, type=parse_iso_date)
    raster.add_argument("--output", required=True, type=Path)
    raster.add_argument(
        "--crs",
        help="metre-based output CRS; defaults to the AOI's UTM zone",
    )
    return parser


def main() -> None:
    """Parse the command, connect to Earth Engine, and run the selected mode."""

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = build_parser().parse_args()
    initialise_earth_engine(args.project, args.authenticate)
    config = RetrievalConfig(scale_m=args.scale)

    if args.command == "raster":
        retrieve_feature_raster(
            args.date,
            args.bbox,
            args.output,
            config,
            args.crs,
        )
        LOGGER.info("Wrote %s and its band-order sidecar", args.output)
        return

    aoi = geometry_from_bbox(args.bbox)
    target_dates = list(iter_dates(args.start_date, args.end_date, args.step_days))
    LOGGER.info("Building samples for %d dates", len(target_dates))

    samples = ee.FeatureCollection([])
    for index, target in enumerate(target_dates):
        daily_samples = sample_training_date(
            target,
            aoi,
            config,
            args.samples_per_class,
            args.seed + index,
        )
        samples = samples.merge(daily_samples)

    output_columns = FEATURE_BANDS + [
        LABEL_BAND,
        "longitude",
        "latitude",
        "date",
        "year",
        "day_of_year",
        "label_source",
        "climate_source",
    ]
    download_feature_collection_csv(samples, args.output, output_columns)
    LOGGER.info("Wrote proxy-labelled training data to %s", args.output)


if __name__ == "__main__":
    main()
