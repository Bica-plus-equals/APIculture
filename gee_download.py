import ee
import geemap

# ee.Authenticate()

# -----------------------------
# Initialize Earth Engine
# -----------------------------

ee.Initialize(project='project-5b26aee2-ba73-4892-90c')


# -----------------------------
# Region of interest
# -----------------------------

romania = (
    ee.FeatureCollection("FAO/GAUL/2015/level0")
    .filter(ee.Filter.eq("ADM0_NAME", "Romania"))
)

# -----------------------------
# Farm geometry
# -----------------------------
farm_geometry = ee.Geometry.Polygon([
    [
        [28.000, 45.030],
        [28.000, 45.010],
        [28.035, 45.010],
        [28.035, 45.030],
        [28.000, 45.030]
    ]
])

# -----------------------------
# Select the dataset function
# -----------------------------

def select_dataset(dataset_name, band, start_date, end_date, roi):

    data = (
        ee.ImageCollection(dataset_name)
        .filterBounds(roi)
        .filterDate(start_date, end_date)
        .select(band)
    )

    return data

temp = select_dataset('MODIS/MOD09GA_006_NDVI','NDVI',
"2023-01-01", "2024-01-01", farm_geometry)
print(temp.size().getInfo())

