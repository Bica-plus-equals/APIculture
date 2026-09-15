import ee
from IPython.display import Image

ee.Authenticate()
ee.Initialize(project='project-5b26aee2-ba73-4892-90c')
#Import dataset

data = ee.ImageCollection('MODIS/061/MCD15A3H')
#initial and final date of interest
i_date = '2023-04-01'
f_date='2023-09-30'

#select data (filters: data, bands)
data = data.select('Lai').filterDate(i_date, f_date)

#Define the location (spatial coords)
farm_geometry = ee.Geometry.Polygon([
    [
        [28.000, 45.030],
        [28.000, 45.010],
        [28.035, 45.010],
        [28.035, 45.030],
        [28.000, 45.030]
    ]
])

#Reduce the data by mean
# lai_img = data.mean()
# lai_img = lai_img.multiply(0.1)

#Reduce data by taking in the first image
lai_img = data.first()
lai_img = lai_img.multiply(0.1)

# Create a URL to the styled image for a region around France.
url = lai_img.getThumbUrl({
    'min': 0, 'max': 6, 'dimensions': 512, 'region': farm_geometry,
    'palette': ['green', 'yellow', 'orange', 'red']})
print(url)

# Display the thumbnail land surface temperature in France.
print('\nPlease wait while the thumbnail loads, it may take a moment...')
Image(url=url)