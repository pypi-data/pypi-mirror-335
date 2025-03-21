# m21ctools

**m21ctools** is a Python library designed to handle cubed-sphere data efficiently. It provides tools for reading, processing, interpolating, and visualizing data from NetCDF-4 files, making it easier to work with cubed-sphere grids in climate, meteorological, and geospatial applications.

## Key Features

### Data Loading and Cleaning
- **Reading NetCDF Files:**  
  Easily read cubed-sphere data from NetCDF-4 files using the `xarray` library with the `h5netcdf` engine.
- **Handling Duplicate Dimensions:**  
  Automatically resolves issues with duplicate 'ncontact' dimension names by replacing them with unique names, ensuring the dataset is ready for analysis.

### Longitude Adjustment
- **Standardizing Coordinates:**  
  Automatically adjusts longitudes to fall within the standard range of -180° to 180°.

### Data Aggregation
- **Combining Data Faces:**  
  Aggregates data from the six faces of the cubed-sphere into flat lists, which simplifies further analysis and processing.

### Interpolation to Regular Grid
- **Grid Interpolation:**  
  Interpolates irregular cubed-sphere data onto a regular latitude-longitude grid using efficient methods from SciPy.

### Visualization
- **Plotting Tools:**  
  Visualizes the interpolated data with contour plots using Matplotlib and Cartopy, complete with coastlines and axis labels.

## Usage Example

Below is a simple example to get you started:

```python
from m21ctools.data_handler import CubedSphereData

# Initialize the CubedSphereData object with your NetCDF file and desired settings.
data_handler = CubedSphereData(
    file_path="path/to/your/datafile.nc4",
    time=0,
    lev=0,
    variable="QV",
    resolution=1.0
)

# Access raw and cleaned data.
raw_data = data_handler.raw_data
clean_data = data_handler.raw_data_cleaned

# Retrieve aggregated latitudes, longitudes, and data as flat 1D arrays.
all_lats, all_lons, all_data = data_handler.all_lats, data_handler.all_lons, data_handler.all_data

# Interpolate data to a uniform latitude-longitude grid.
lat_grid, lon_grid, data_grid = data_handler.interpolate_to_latlon_grid(method='linear')  # Default interpolation method is 'linear'

# Visualize the data.
data_handler.plot_data(lat_grid, lon_grid, data_grid)
