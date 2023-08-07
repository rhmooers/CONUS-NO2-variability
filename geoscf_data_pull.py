#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  6 11:50:32 2022

@author: rhmooers

modified from code by jgeddes 
"""

import xarray as xr
import numpy as np
import pickle
import datetime
import calendar

url_dir = "https://opendap.nccs.nasa.gov/dods/gmao/geos-cf/assim/"
url_aqc = "aqc_tavg_1hr_g1440x721_v1"
url_chm = "chm_tavg_1hr_g1440x721_v1"
url_xgc = "xgc_tavg_1hr_g1440x721_x1"
url_met = 'met_tavg_1hr_g1440x721_x1'

url = url_dir + url_aqc 
ds = xr.open_dataset(url)

# Decide on up your lat/lon slice boundaries
min_lon = -130
min_lat = 22
max_lon = -59
max_lat = 53
 
# year/months of data 
years = [2020]
months = np.array([12])

for y in years:
    for m in months:
        d_last = datetime.date(y, m, calendar.monthrange(y, m)[-1]).day

        first_datestring = str(y)+'-'+str(m).zfill(2)+'-'+'01'
        last_datestring = str(y)+'-'+str(m).zfill(2)+'-'+str(d_last).zfill(2)
        
        # Retrieve the output over that area slice for NO2:
        no2 = ds.no2.sel(lon=slice(min_lon, max_lon), 
                         lat=slice(min_lat, max_lat), 
                         time=slice(first_datestring, last_datestring) )

        S = np.shape(no2)
        NN = S[0]
        nlat = S[2]
        nlon = S[3]

        no2_arr = np.zeros((NN, nlat, nlon))
        no2_dat = np.empty(NN, dtype='datetime64[s]')
        no2_dat[:] = np.datetime64('1970-01-01T00:30:00')


        for i in range(NN):
            no2_arr[i,:,:] = np.squeeze(no2[i].values)
            no2_dat[i] = no2[i].time.values
            print ('no2 aqc', no2_dat[i])
        
        no2_store = {'no2_arr':no2_arr, 'no2_dat':no2_dat}
    
        file_out = open("/projectnb/atmchem/rhmooers/geoscf/geocf_no2usa_"+str(y)+str(m).zfill(2)+".pkl", "wb")
        pickle.dump(no2_store, file_out)
        

url = url_dir + url_xgc 
ds = xr.open_dataset(url)


for y in years:
    for m in months:
        d_last = datetime.date(y, m, calendar.monthrange(y, m)[-1]).day

        first_datestring = str(y)+'-'+str(m).zfill(2)+'-'+'01'
        last_datestring = str(y)+'-'+str(m).zfill(2)+'-'+str(d_last).zfill(2)
        
        # Retrieve the output over that area slice for NO2:
        no2 = ds.tropcol_no2.sel(lon=slice(min_lon, max_lon), 
                                 lat=slice(min_lat, max_lat), 
                                 time=slice(first_datestring, last_datestring) )

        S = np.shape(no2)
        NN = S[0]
        nlat = S[1]
        nlon = S[2]

        no2_arr = np.zeros((NN, nlat, nlon))
        no2_dat = np.empty(NN, dtype='datetime64[s]')
        no2_dat[:] = np.datetime64('1970-01-01T00:30:00')


        for i in range(NN):
            no2_arr[i,:,:] = np.squeeze(no2[i].values)
            no2_dat[i] = no2[i].time.values
            print ('no2 aqc', no2_dat[i])
        
        no2_store = {'no2_arr':no2_arr, 'no2_dat':no2_dat}
    
        file_out = open("/projectnb/atmchem/rhmooers/geoscf/geocf_trpcolusa_"+str(y)+str(m).zfill(2)+".pkl", "wb")
        pickle.dump(no2_store, file_out)


url = url_dir + url_met 
ds = xr.open_dataset(url)


for y in years:
    for m in months:
        d_last = datetime.date(y, m, calendar.monthrange(y, m)[-1]).day

        first_datestring = str(y)+'-'+str(m).zfill(2)+'-'+'01'
        last_datestring = str(y)+'-'+str(m).zfill(2)+'-'+str(d_last).zfill(2)
        
        # Retrieve the output over that area slice for NO2:
        t10 = ds.t10m.sel(lon=slice(min_lon, max_lon), 
                          lat=slice(min_lat, max_lat), 
                          time=slice(first_datestring, last_datestring) )

        S = np.shape(t10)
        NN = S[0]
        nlat = S[1]
        nlon = S[2]

        t10_arr = np.zeros((NN, nlat, nlon))
        t10_dat = np.empty(NN, dtype='datetime64[s]')
        t10_dat[:] = np.datetime64('1970-01-01T00:30:00')


        for i in range(NN):
            t10_arr[i,:,:] = np.squeeze(t10[i].values)
            t10_dat[i] = t10[i].time.values
            print ('no2 aqc', t10_dat[i])
        
        t10_store = {'t10_arr':t10_arr, 't10_dat':t10_dat}
    
        file_out = open("/projectnb/atmchem/rhmooers/geoscf/geocf_t10usa_"+str(y)+str(m).zfill(2)+".pkl", "wb")
        pickle.dump(t10_store, file_out)
    

# Example code to open the pickle files:
example_filename='"/projectnb/atmchem/rhmooers/geoscf/geocf_trpcolusa_201905.pkl'
no2_dict = pickle.load(open(example_filename, "rb"))

# Check contents of dictionary
print(no2_dict.keys())
print('no2_arr shape', np.shape(no2_dict['no2_arr']))
print('no2_dat (datetime) shape', np.shape(no2_dict['no2_dat']))