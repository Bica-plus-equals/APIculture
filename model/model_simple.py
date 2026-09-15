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

from pathlib import Path
import numpy as np
import rasterio
import torch
from torch.utils.data import Dataset, DataLoader

class RasterDataset(Dataset):
    def __init__(self, X, y):
        self.X = X
        self.y = y

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        x = torch.tensor(self.X[idx], dtype=torch.float32) #should we add a channel dimention?
        y = torch.tensor(self.y[idx], dtype=torch.float32)

        return x, y

project_root = Path(__file__).parent.parent
data_folder = project_root / "data" / "GEE Data" 

tif_files = sorted(data_folder.glob("*.tif"))

print("Number of files:", len(tif_files))

images = []

with rasterio.open(tif_files[0]) as src:
    print("Width:", src.width)
    print("Height:", src.height)
    print("Bands:", src.count)
    print("CRS:", src.crs)
    print("Data type:", src.dtypes[0])
    print("Image dimensions:", src.shape)

for file in tif_files:
    with rasterio.open(file) as src:
        image = src.read(1)  # Read the first band
        images.append(image)
images = np.array(images)

X = images[:-1]
y = images[1:]

#Add CNN channels (batch, channels, height, width)
X = X[:, None, :, :]
y = y[:, None, :, :]

dataset = RasterDataset(X, y)

print("Images:", images.shape)
print("X:", X.shape)
print("y:", y.shape)
