#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  1 13:59:22 2023

@author: rhmooers
"""

##### Data Processing to Obtain Daily Afternoon Averages of GEOS-CF Data #####

# extracting 12pm to 3pm local time to obtain daily "afternoon averages" 
# note that since the model is in UTC there will be missing local time...
 # ...data on the last day of data 

import numpy as np  
import xarray as xr
import pandas as pd
import calendar 
import pickle
import os, fnmatch
from pathlib import Path
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from datetime import datetime, timedelta

# reading in latitude and longitude arrays 
url_dir = "https://opendap.nccs.nasa.gov/dods/gmao/geos-cf/assim/"
url_aqc = "aqc_tavg_1hr_g1440x721_v1"
url = url_dir + url_aqc 
ds = xr.open_dataset(url)

# Decide on up your lat/lon slice boundaries
min_lon = -126
min_lat = 25
max_lon = -60
max_lat = 60

# date to extract lat/lon arrays from 
# arbitrary since it is equal for all dates 
y = 2018
m = 2
d_last = 2

first_datestring = str(y)+'-'+str(m).zfill(2)+'-'+'01'
last_datestring = str(y)+'-'+str(m).zfill(2)+'-'+str(
    d_last).zfill(2)

# Retrieve the output over the area slice for NO2:
no2 = ds.no2.sel(lon=slice(min_lon, max_lon), 
                 lat=slice(min_lat, max_lat), 
                 time=slice(first_datestring, 
                            last_datestring))

# storing latitude and lonigitude values in numpy arrays 
lat_array = no2.lat.values
lon_array = no2.lon.values


################# Reading in GEOS-CF NO2 and Temperature Data ################

# grouping data files by variable 
geoscf_usa_path = Path('/projectnb/atmchem/shared/geocf_usa')
no2_files = geoscf_usa_path.glob('*no2usa*')
column_files = geoscf_usa_path.glob('*trpcolusa*')
temp_files = geoscf_usa_path.glob('*t10usa*')

# saving filepaths as strings in lists 
no2_filelist = [] # to store no2 paths 
for i in no2_files: 
    no2_filelist.append(str(i))
column_filelist = [] # to store col no2 paths 
for i in column_files: 
    column_filelist.append(str(i))
temp_filelist = [] # to store temperature paths 
for i in temp_files: 
    temp_filelist.append(str(i))

# sorting filenames into temporal order 
def filename_sort(filelist):
    filelist_sorted = []
    for x in sorted(filelist):
        filelist_sorted.append(x)
    return filelist_sorted

# this sorts the path names by dates in the lists 
no2_filelist = filename_sort(no2_filelist)
column_filelist = filename_sort(column_filelist)
temp_filelist = filename_sort(temp_filelist)

# function to store data as dictionaries in lists 
def data_dictionary_store(file_list):
    dict_list = []
    for string_path in file_list:
        path = os.path.abspath(string_path)
        dict_list.append(pickle.load(open(path, "rb")))
    return dict_list

# storing the data 
no2_list = data_dictionary_store(no2_filelist)
column_list = data_dictionary_store(column_filelist)
temp_list = data_dictionary_store(temp_filelist)


######################## Converting Data to Xarray ###########################

# latitude and longitude as lists for xarray dimensions
lat_list = np.ndarray.tolist(lat_array)
lon_list = np.ndarray.tolist(lon_array)

# function to convert dictionaries in list to xarrays in list
def dict_to_array(data_list, date_key, data_key):
    array_list = []
    for i in range(len(data_list)):
        times = np.ndarray.tolist(
            data_list[i].get(date_key))
        data_array = xr.DataArray(
            data_list[i].get(data_key), 
            coords=[("time", times,), 
                    ("lat", lat_list), 
                    ("lon", lon_list)])
        array_list.append(data_array)   
    return array_list

# converting no2, temp, and column dictionaries to xarrays 
no2_array_list = dict_to_array(no2_list, 
                               'no2_dat', 'no2_arr')
column_array_list = dict_to_array(column_list, 
                                  'no2_dat', 'no2_arr')
temp_array_list = dict_to_array(temp_list, 
                                't10_dat', 't10_arr')

# concatenating along time axes to obtain a single xarray for each variable 
no2_array = no2_array_list[0]
for i in range(1, len(no2_array_list)): 
    no2_array =  xr.concat([no2_array, 
                            no2_array_list[i]], 
                           dim='time')

column_array = column_array_list[0]
for i in range(1, len(column_array_list)): 
    column_array =  xr.concat([column_array, 
                               column_array_list[i]], 
                              dim='time')

temp_array = temp_array_list[0]
for i in range(1, len(temp_array_list)): 
    temp_array = xr.concat([temp_array,
                            temp_array_list[i]], 
                           dim='time')
    
    
############# UTC to Local Time Conversions based on Longitude ###############

# Convention for time adjustments:  
# -60 +- 7.5 degrees (52.5-67.5) = UTC - 4   
# -75 +- 7.5 degrees (67.5-82.5) = UTC - 5   
# -90 +- 7.5 degrees (82.5-97.5) = UTC - 6  
# -105 +- 7.5 degrees (97.5-112.5) = UTC - 7   
# -120 +- 7.5 degrees (112.5-127.5) = UTC - 8  

# function to change times from UTC to local 
# splits the array into smaller arrays, each with respective local times
def time_adjust(array): 
    
    timezone1 = array.sel(lon=slice(-126., -112.5)) # UTC - 8
    adjustedtime1 = []
    for j in range(len(timezone1.time.values)): 
        timestamp = timezone1.time.values[j]
        timestamp = datetime.utcfromtimestamp(int(timestamp)/1e9)
        new_time = timestamp - timedelta(hours = 8)
        adjustedtime1.append(new_time)

    timezone2 = array.sel(lon=slice(-112.25, -97.5)) # UTC - 7
    adjustedtime2 = []
    for j in range(len(timezone2.time.values)): 
        timestamp = timezone2.time.values[j]
        timestamp = datetime.utcfromtimestamp(int(timestamp)/1e9)
        new_time = timestamp - timedelta(hours = 7)
        adjustedtime2.append(new_time)

    timezone3 = array.sel(lon=slice(-97.25, -82.5)) # UTC - 6 
    adjustedtime3 = []
    for j in range(len(timezone3.time.values)): 
        timestamp = timezone3.time.values[j]
        timestamp = datetime.utcfromtimestamp(int(timestamp)/1e9)
        new_time = timestamp - timedelta(hours = 6)
        adjustedtime3.append(new_time)

    timezone4 = array.sel(lon=slice(-82.25, -67.5)) # UTC - 5
    adjustedtime4 = []
    for j in range(len(timezone4.time.values)): 
        timestamp = timezone4.time.values[j]
        timestamp = datetime.utcfromtimestamp(int(timestamp)/1e9)
        new_time = timestamp - timedelta(hours = 5)
        adjustedtime4.append(new_time)

    timezone5 = array.sel(lon=slice(-67.25, -60.)) # UTC - 4
    adjustedtime5 = []
    for j in range(len(timezone5.time.values)): 
        timestamp = timezone5.time.values[j]
        timestamp = datetime.utcfromtimestamp(int(timestamp)/1e9)
        new_time = timestamp - timedelta(hours = 4)
        adjustedtime5.append(new_time)
    
    # splitting lat and lon values to re-attatch to arrays 
    lat1 = np.ndarray.tolist(timezone1.coords['lat'].values)
    lon1 = np.ndarray.tolist(timezone1.coords['lon'].values)
    
    lat2 = np.ndarray.tolist(timezone2.coords['lat'].values)
    lon2 = np.ndarray.tolist(timezone2.coords['lon'].values)
    
    lat3 = np.ndarray.tolist(timezone3.coords['lat'].values)
    lon3 = np.ndarray.tolist(timezone3.coords['lon'].values)
    
    lat4 = np.ndarray.tolist(timezone4.coords['lat'].values)
    lon4 = np.ndarray.tolist(timezone4.coords['lon'].values)
    
    lat5 = np.ndarray.tolist(timezone5.coords['lat'].values)
    lon5 = np.ndarray.tolist(timezone5.coords['lon'].values)
    
    # compiling split/adjusted data into timezone arrays 
    timezone1 = xr.DataArray(timezone1, 
                            coords=[("time", adjustedtime1,), 
                            ("lat", lat1), ("lon", lon1)])
    
    timezone2 = xr.DataArray(timezone2, 
                            coords=[("time", adjustedtime2,), 
                            ("lat", lat2), ("lon", lon2)])
    
    timezone3 = xr.DataArray(timezone3, 
                            coords=[("time", adjustedtime3,), 
                            ("lat", lat3), ("lon", lon3)])
    
    timezone4 = xr.DataArray(timezone4, 
                            coords=[("time", adjustedtime4,), 
                            ("lat", lat4), ("lon", lon4)])
    
    timezone5 = xr.DataArray(timezone5, 
                            coords=[("time", adjustedtime5,), 
                            ("lat", lat5), ("lon", lon5)])
    
    timezone_list = [timezone1, timezone2, timezone3, 
                     timezone4, timezone5]
    
    return timezone_list

# no2 data split by timezone
# data is in local time
adjusted_no2_arrays = time_adjust(no2_array)
no2_array1 = adjusted_no2_arrays[0]
no2_array2 = adjusted_no2_arrays[1]
no2_array3 = adjusted_no2_arrays[2]
no2_array4 = adjusted_no2_arrays[3]
no2_array5 = adjusted_no2_arrays[4]

# column data split by timezone and with local time 
adjusted_column_arrays = time_adjust(column_array)
column_array1 = adjusted_column_arrays[0]
column_array2 = adjusted_column_arrays[1]
column_array3 = adjusted_column_arrays[2]
column_array4 = adjusted_column_arrays[3]
column_array5 = adjusted_column_arrays[4]

# temp data split by timezone and with local time 
adjusted_temp_arrays = time_adjust(temp_array)
temp_array1 = adjusted_temp_arrays[0]
temp_array2 = adjusted_temp_arrays[1]
temp_array3 = adjusted_temp_arrays[2]
temp_array4 = adjusted_temp_arrays[3]
temp_array5 = adjusted_temp_arrays[4]


#################### Extracting 12pm to 3pm Local Time #######################
    
# function to take afternoon averages 
# output is an xarray with daily "afternoon" (1-3pm) averages 
def afternoon_average(array): 
    
    dates_list = []
    for i in range(len(array.time.values)):
        timestamp = array.time.values[i]
        unix_time = timestamp.astype(datetime)
        dt_time = datetime.fromtimestamp(unix_time/1e9)
        dates_list.append(dt_time)   

    # separating out hour of day 
    hours = []
    for i in range(len(array.time.values)):
        timestamp = array.time.values[i]
        unix_time = timestamp.astype(datetime)
        dt_time = datetime.fromtimestamp(unix_time/1e9)
        only_hour = dt_time.hour
        hours.append(only_hour)

    # replace time in xarray with only hour
    array.reset_index(['time'], drop = True)
    array.coords['time'] = hours
    array = array.rename({'time': 'hours'})

    # creating mask where 1 = afternoon times and 0 = other times
    mask = []
    for i in array['hours']: 
        if i == 12 or i == 13 or i == 14 or i == 15: 
            mask.append(1)
        else: 
            mask.append(0)

    # replacing time in xarrays with mask  
    array.reset_index(['hours'], drop = True)
    array.coords['hours'] = mask
    masked_array = array.rename({'hours': 'mask'})

    # creating pandas dataframe with dates and mask 
    dates = np.array(dates_list)
    afternoon_df = pd.DataFrame({'Dates': dates})
    afternoon_df['mask'] = mask 
    afternoon_df

    afternoon_dates = afternoon_df[afternoon_df['mask'] 
                                   == 1]['Dates'].to_list()
    print(afternoon_dates)

    # filtering xarray to only afternoon 
    array_new = masked_array[(masked_array['mask']==1)]

    # replace mask coord with dates coord
    array_new.reset_index(['mask'], drop = True)
    array_new.coords['mask'] = afternoon_dates
    array_new = array_new.rename({'mask': 'date'})

    # using resample to take daily afternoon averages
    afternoon_ave = array_new.resample(date='1D').mean()

    return afternoon_ave

# uses function to take afternoon ave of all data
# then concatenates along longitude axis back into one array 

# afternoon averages of no2 for each timezone 
no2_ave1 = afternoon_average(no2_array1)
no2_ave2 = afternoon_average(no2_array2)
no2_ave3 = afternoon_average(no2_array3)
no2_ave4 = afternoon_average(no2_array4)
no2_ave5 = afternoon_average(no2_array5)

# concatenating into a single array
# timezone is now irrelevant...
# ...since values are all based on local time 
afternoon_ave_no2 = xr.concat(
    [no2_ave1, no2_ave2, no2_ave3, no2_ave4, no2_ave5],
    dim='lon')

# afternoon averages of column no2
column_ave1 = afternoon_average(column_array1)
column_ave2 = afternoon_average(column_array2)
column_ave3 = afternoon_average(column_array3)
column_ave4 = afternoon_average(column_array4)
column_ave5 = afternoon_average(column_array5) 

# concatenating into a single array
afternoon_ave_column = xr.concat(
    [column_ave1, column_ave2, column_ave3, column_ave4, 
     column_ave5], dim='lon')

# afternoon temperature averages 
temp_ave1 = afternoon_average(temp_array1)
temp_ave2 = afternoon_average(temp_array2)
temp_ave3 = afternoon_average(temp_array3)
temp_ave4 = afternoon_average(temp_array4)
temp_ave5 = afternoon_average(temp_array5)

# concatenating into a single array
afternoon_ave_temp = xr.concat(
    [temp_ave1, temp_ave2, temp_ave3, temp_ave4, temp_ave5], 
    dim='lon')

# saving afternoon average arrays as pickle files 
no2_store = {'no2_ave': afternoon_ave_no2}
file_out = open("/projectnb/atmchem/shared/geocf_usa/geocf_afternoon_ave_no2.pkl", "wb")
pickle.dump(no2_store, file_out)
                
col_store = {'col_ave': afternoon_ave_column}
file_out = open("/projectnb/atmchem/shared/geocf_usa/geocf_afternoon_ave_column.pkl", "wb")
pickle.dump(col_store, file_out)

temp_store = {'temp_ave': afternoon_ave_temp}
file_out = open("/projectnb/atmchem/shared/geocf_usa/geocf_afternoon_ave_temp.pkl", "wb")
pickle.dump(temp_store, file_out)