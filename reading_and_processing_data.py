#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 14:27:56 2023

@author: rhmooers
"""

import numpy as np  
import xarray as xr
import pandas as pd 
import geopandas as gpd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pickle
import os


#################### Reading in GEOS-CF and TROPOMI data #####################

def GeosCF_Tropomi_Read(geoscf_files_path, tropomi_files_path): 
    
    ################################ GEOS-CF #################################

    # reading in aftenoon averaged GEOS-CF data 
    # processing code in: nox_temp_correlation_data_processing.pynb
    geoscf_usa_path = geoscf_files_path
    
    # loading no2 data in lowest gridbox
    afternoon_no2_data = pickle.load(open(
        geoscf_usa_path+'geocf_afternoon_ave_no2.pkl', "rb"))
    # storing afternoon ave data as array
    afternoon_no2_array_0 = afternoon_no2_data['no2_ave'] 
    
    # converting values to same units as tropomi, molec/cm^3
    afternoon_no2_array = afternoon_no2_array_0 * 1e15     
    
    # loading column no2 data
    afternoon_column_data = pickle.load(open(
        geoscf_usa_path+'geocf_afternoon_ave_column.pkl', "rb")) 
    # storing afternoon column data as array
    afternoon_column_array_0 = afternoon_column_data['col_ave']  
    
    # converting values to same units as tropomi,  molec/cm^3 
    afternoon_column_array = afternoon_column_array_0 * 1e15  
    
    # loading temperature data
    afternoon_temp_data = pickle.load(open(
        geoscf_usa_path+'geocf_afternoon_ave_temp.pkl', "rb")) 
    # storing temperature data as array 
    afternoon_temp_array = afternoon_temp_data['temp_ave']
    

   ################################ TROPOMI ##################################

    # reading in TROPOMI data regridded to align with GEOS-CF
    # regridding code from Kang Sun at University at Buffalo, NY

    # retrieving names of all regridded files in a list 
    filepath = tropomi_files_path
    tropomi_filename_list = os.listdir(filepath) 
    
    # sorting filenames by date 
    tropomi_filename_list_sorted = [] 
    for x in sorted(tropomi_filename_list):
        tropomi_filename_list_sorted.append(x)
    
    # reading in each file as an xarray 
    def netcdf_to_xarray(filepath, filename): 
        xarray = xr.open_dataset(filepath+'/'+filename, 
                                 engine='netcdf4')
        return xarray 
    
    # storing xarrays in a list for now 
    tropomi_array_list = []
    for filename in tropomi_filename_list_sorted: 
        array = netcdf_to_xarray(filepath, filename)
        no2_array = array.value
        tropomi_array_list.append(no2_array)
        
    # sorted lists of directory contents 
    new_trop_path = '/projectnb/atmchem/rhmooers/tropomi_regrid/'
    dir_list = sorted(os.listdir(new_trop_path))
    
    raw_data_dir = '/projectnb/atmchem/shared/tropomi/tropomi_pal/conus/'
    raw_dir_list = sorted(os.listdir(raw_data_dir))
    
    # concatenating tropomi xarrays along time axis 
    tropomi_array = tropomi_array_list[0]
    for i in range(1, len(tropomi_array_list)): 
        tropomi_array =  xr.concat([tropomi_array, 
                                    tropomi_array_list[i]], 
                                   dim='time')
        
    # creating date array to attatch to tropomi array
    # extracting first date from filename 
    filepath = tropomi_files_path
    first_file_string = str(os.listdir(filepath)[0])
    date_string = first_file_string[-11:-3] # start date 
    first_date = datetime.strptime(date_string, '%Y%d%m') # in dt format 
    # create list of dates with length equal to lenth of concatenated array
    # -1 to length accounts for exclusion of last day of data...
    # ...due to missing values when converted from UTC to local time
    date_list = [first_date + timedelta(days=x) 
                 for x in range(len(tropomi_array.time.values)-1)]
    
    # changing time coordinate to dates list 
    tropomi_array.reset_index(['time'], drop = True)
    end_len = len(tropomi_array.time.values)-1
    tropomi_array = tropomi_array.isel(time=slice(0, end_len))
    tropomi_array.coords['time'] = date_list
    tropomi_array = tropomi_array.rename({'time': 'date'})
    # time coordinate now contains dates in datetime format 


    ########## adjusting the lat and lon on both datasets to match ###########
    
    # spatial max and min for tropomi and geoscf 
    tropomi_min_lat = tropomi_array.lat.values.min()
    tropomi_max_lat = tropomi_array.lat.values.max()
    tropomi_min_lon = tropomi_array.lon.values.min()
    tropomi_max_lon = tropomi_array.lon.values.max()
    geoscf_min_lat = afternoon_no2_array.lat.values.min()
    geoscf_max_lat = afternoon_no2_array.lat.values.max()
    geoscf_min_lon = afternoon_no2_array.lon.values.min()
    geoscf_max_lon = afternoon_no2_array.lon.values.max()
    
    # finding boundaries shared by datasets 
    min_lat = max(tropomi_min_lat, geoscf_min_lat)
    max_lat = min(tropomi_max_lat, geoscf_max_lat)
    min_lon = max(tropomi_min_lon, geoscf_min_lon)
    max_lon = min(tropomi_max_lon, geoscf_max_lon)
    
    # extracting earliest and latest dates from each dataset
    trop_firstdate = tropomi_array.date.values[0]
    trop_lastdate = tropomi_array.date.values[len(
        tropomi_array.date.values)-1]
    geos_firstdate1 = afternoon_no2_array.date.values[0]
    geos_lastdate1 = afternoon_no2_array.date.values[len(
        afternoon_no2_array.date.values)-1]
    geos_firstdate2 = afternoon_column_array.date.values[0]
    geos_lastdate2 = afternoon_column_array.date.values[len(
        afternoon_column_array.date.values)-1]
    geos_firstdate3 = afternoon_temp_array.date.values[0]
    geos_lastdate3 = afternoon_temp_array.date.values[len(
        afternoon_temp_array.date.values)-1]
    
    # selecting date range for which all datasets overlap
    firstdate = max([trop_firstdate, geos_firstdate1, 
                     geos_firstdate2, geos_firstdate3])
    lastdate = min([trop_lastdate, geos_lastdate1, 
                    geos_lastdate2, geos_lastdate3]) 
    # ^excluding last day becasue of NaN values in GEOS-CF dataset
    
    # cropped tropomi column NO2
    tropomi_col_no2 = tropomi_array.sel(lat=slice(min_lat, 
                                                  max_lat),
                                        lon=slice(min_lon, 
                                                  max_lon), 
                                        date=slice(firstdate,
                                                   lastdate))
    # cropped geoscf lowest-gridbox NO2
    geoscf_surf_no2 = afternoon_no2_array.sel(lat=slice(min_lat, 
                                                        max_lat),
                                              lon=slice(min_lon, 
                                                        max_lon), 
                                             date=slice(firstdate,
                                                        lastdate))
    # cropped geoscf column NO2
    geoscf_col_no2 = afternoon_column_array.sel(lat=slice(min_lat, 
                                                          max_lat),
                                                lon=slice(min_lon, 
                                                          max_lon), 
                                               date=slice(firstdate,
                                                          lastdate))
    # cropped geoscf temperature 
    geoscf_temp = afternoon_temp_array.sel(lat=slice(min_lat, 
                                                     max_lat),
                                            lon=slice(min_lon, 
                                                      max_lon), 
                                          date=slice(firstdate,
                                                     lastdate))
    
    
    ########## Filtering daily GEOS-CF data by TROPOMI cloud cover ###########
    
    # filtering data so values that are excluded from... 
    # TROPOMI due to cloud cover are also excluded from GEOS-CF 
    
    # creating mask for locations of NaN values in TROPOMI array 
    # nan locations are 1, all other data locations are 0
    tropomi_col_no2_copy = tropomi_col_no2.copy(deep=True)
    tropomi_mask = tropomi_col_no2_copy.notnull()
    
    # applying the mask to change geos-cf values...
    # ...to nan where tropomi values are nan
    geoscf_col_no2_masked = xr.where(tropomi_mask == True, 
                                     geoscf_col_no2, 
                                     tropomi_col_no2)
    geoscf_surf_no2_masked = xr.where(tropomi_mask == True, 
                                      geoscf_surf_no2, 
                                      tropomi_col_no2)
    geoscf_temp_masked = xr.where(tropomi_mask == True, 
                                  geoscf_temp, 
                                  tropomi_col_no2)
    
    return (tropomi_col_no2, geoscf_col_no2, 
            geoscf_surf_no2, geoscf_temp, 
            geoscf_col_no2_masked, geoscf_surf_no2_masked, 
            geoscf_temp_masked)
    

# testing geos-cf and tropomi reading function 
'''
(tropomi_col_no2, geoscf_col_no2, geoscf_surf_no2, geoscf_temp, geoscf_col_no2_masked, 
 geoscf_surf_no2_masked, geoscf_temp_masked) = GeosCF_Tropomi_Read(
     '/projectnb/atmchem/shared/geocf_usa/', 
     '/projectnb/atmchem/shared/tropomi/tropomi_pal/conus/gridded_geoscf')
'''


############################### Shapefiles ###################################

def Shapefile_Read(us_path, can_path, mex_path):

    # United States 
    us_file = us_path
    us = gpd.read_file(us_file)
    us.to_crs('EPSG:4326', inplace=True)
    
    # Canada 
    can_file = can_path
    can = gpd.read_file(can_file)
    can.to_crs('EPSG:4326', inplace=True)
    
    # Mexico 
    mex_file = mex_path
    mex = gpd.read_file(mex_file)
    mex.to_crs('EPSG:4326', inplace=True)
    
    # combinimg dataframes for all three countries 
    us['country'] = 'United States'
    can['country'] = 'Canada'
    mex['country'] = 'Mexico'
    
    us.rename(columns={'NAME': 'name'}, inplace=True)
    can.rename(columns={'PRENAME': 'name'}, inplace=True)
    mex.rename(columns={'ADM1_ES': 'name'}, inplace=True)
    
    us = us[['name', 'country', 'geometry']]
    can = can[['name', 'country', 'geometry']]
    mex = mex[['name', 'country', 'geometry']]
    
    states = pd.concat([us, can, mex])
    states = gpd.GeoDataFrame(states, geometry=states['geometry'], crs='EPSG:4326')
    
    return states 


# testing shapefile function 
'''
states = Shapefile_Read('/projectnb/atmchem/shared/shapefiles/cb_2018_us_state_500k/cb_2018_us_state_500k.shp', 
               '/projectnb/atmchem/rhmooers/shapefiles/canada/lpr_000b16a_e.shp', 
               '/projectnb/atmchem/rhmooers/shapefiles/mexico/mex_admbnda_adm1_govmex_20210618.shp')

states.plot(color='None', edgecolor='k')
plt.show()
'''
