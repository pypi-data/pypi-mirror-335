"""
data_handler.py

This module provides the CubedSphereData class, designed to read, process, interpolate, 
and visualize 2D cubed-sphere data from NetCDF files.

Usage:
    from data_handler import CubedSphereData
"""

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from scipy.interpolate import griddata

import warnings
warnings.filterwarnings("ignore")

class CubedSphereData:
    def __init__(self, file_path, time=0, lev=0, variable="QV", resolution=1.0):
        """
        Handles reading, processing, interpolating, and visualizing 2D cubed-sphere data from cubed-sphere (.nc4) files.

        Parameters:
        - file_path (str): Path to the NetCDF file.
        - time (int): Time index to extract, default 0
        - lev (int): Level index to extract, default 0
        - variable (str): The variable to extract, default "QV"
        - resolution (float): Grid resolution in degrees for interpolation, default 1.0
        """
        self.file_path = file_path
        self.time = time
        self.lev = lev
        self.variable = variable
        self.resolution = resolution
        self.lats = None
        self.lons = None
        self.data = None
        self.lat_grid = None
        self.lon_grid = None
        self.data_grid = None
        self.raw_data = None
        self.raw_data_cleaned = None

        self.load_data()
        
    # Load data
    def load_data(self):
        """Reads the NetCDF file and extracts data (lats, lons, and a user asigned
        variable at a give time and level), handling duplicate 'anchor' dimensions."""
        with xr.open_dataset(self.file_path, engine="h5netcdf") as ds:
            # Rename duplicate dimensions as the 'anchor' variable have duplicate dimensions - (nf, ncontact, ncontact)
            self.raw_data = ds.copy()
            anchor = ds['anchor']
            anchor_corrected = xr.DataArray(data=anchor.values, dims=('nf', 'ncontact1', 'ncontact2'), attrs=anchor.attrs)
            ds['anchor'] = anchor_corrected

            self.raw_data_cleaned = ds
            self.lats = ds["lats"].values
            self.lons = ds["lons"].values
            self.data = ds[self.variable].isel(time=self.time, lev=self.lev).values

        # Adjust longitudes
        self.lons = self.adjust_longitudes(self.lons)

        # Aggregate data from the cubed sphere
        self.all_lats, self.all_lons, self.all_data = self.aggregate_data()

    @staticmethod
    def adjust_longitudes(lons):
        """Adjusts longitudes to be within the range [-180, 180]."""
        return np.where(lons > 180, lons - 360, lons)

    def aggregate_data(self):
        """Aggregates the data across the six faces of the cubed sphere into flat lists.
        Returns:
        tuple: Lists of latitudes, longitudes, and corresponding data values."""
        all_lats, all_lons, all_data = [], [], []
        for face_index in range(self.data.shape[0]):  
            face_lats = self.lats[face_index, :, :].flatten()
            face_lons = self.lons[face_index, :, :].flatten()
            face_data = self.data[face_index, :, :].flatten()

            all_lats.extend(face_lats)
            all_lons.extend(face_lons)
            all_data.extend(face_data)

        return all_lats, all_lons, all_data

    def interpolate_to_latlon_grid(self, method='linear'):
        """Interpolates the data to a regular latitude-longitude grid.
        Returns:
        tuple: Interpolated latitude grid, longitude grid, and data grid arrays."""
        lat_grid = np.arange(-90, 90 + self.resolution, self.resolution)
        lon_grid = np.arange(-180, 180 + self.resolution, self.resolution)
        lon_grid, lat_grid = np.meshgrid(lon_grid, lat_grid)

        # Perform interpolation
        data_grid = griddata((self.all_lats, self.all_lons), self.all_data, (lat_grid, lon_grid), method=method)

        self.lat_grid, self.lon_grid, self.data_grid = lat_grid, lon_grid, data_grid
        return lat_grid, lon_grid, data_grid

    @staticmethod
    def plot_data(lat_grid, lon_grid, data_grid):
        """Plots the interpolated data on a latitude-longitude grid with labeled axes."""

        fig = plt.figure(figsize=(10, 5))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.coastlines()

        contour = plt.contourf(
            lon_grid, lat_grid, data_grid * 1e3, 
            60, transform=ccrs.PlateCarree(), cmap='GnBu'
        )

        plt.colorbar(contour, label='Specific Humidity (g kg⁻¹)')
        
        # Set axis labels and ticks
        ax.set_xlabel('Longitude', fontsize=12)
        ax.set_ylabel('Latitude', fontsize=12)
        lon_ticks = range(-180, 181, 30)  # Longitude from -180 to 180, step 30°
        lat_ticks = range(-90, 91, 30)    # Latitude from -90 to 90, step 30°
        ax.set_xticks(lon_ticks)
        ax.set_yticks(lat_ticks)
        ax.set_xticklabels(lon_ticks, fontsize=10)
        ax.set_yticklabels(lat_ticks, fontsize=10)

        plt.title('Specific Humidity on Latitude-Longitude Grid', fontsize=14)
        fig.savefig('specific_humidity.png')
        plt.show()

