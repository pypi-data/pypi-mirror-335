# -*- coding: utf-8 -*-
""" plotting example
"""

from data_handler import CubedSphereData 

# calculate

file_path = '../../../gmao/data/e5303_m21c_jan18.lmv_inst_1hr_glo_C360x360x6_slv.2018-01-31T0000Z.nc4'
data_handler = CubedSphereData(file_path=file_path, time=0, lev=0, variable="QV", resolution=1.0)

raw_data = data_handler.raw_data

clean_data = data_handler.raw_data_cleaned


lat_grid, lon_grid, data_grid = data_handler.interpolate_to_latlon_grid(method='linear')

data_handler.plot_data(lat_grid, lon_grid, data_grid)