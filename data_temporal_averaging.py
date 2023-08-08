#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 14:55:06 2023

@author: rhmooers
"""

import calendar
import matplotlib.cm as cm
import reading_and_processing_data as read
import plotting_functions as pf


# reading in data 
(tropomi_col_no2, geoscf_col_no2, geoscf_surf_no2, geoscf_temp, geoscf_col_no2_masked, 
 geoscf_surf_no2_masked, geoscf_temp_masked) = read.GeosCF_Tropomi_Read(
     '/projectnb/atmchem/shared/geocf_usa/', 
     '/projectnb/atmchem/shared/tropomi/tropomi_pal/conus/gridded_geoscf')

######## Tallying the number of days of data per pixel for each month ########

def Days_of_Data(tropomi_dataset): 
    
    # creating mask for locations of NaN values in TROPOMI array 
    # nan locations are 1, all other data locations are 0
    tropomi_dataset_copy = tropomi_dataset.copy(deep=True)
    tropomi_mask = tropomi_dataset_copy.notnull()
    
    # tallying the number of days of data per pixel for each month 
    days_with_data_month = tropomi_mask.resample(date='M').sum()
    # and for the whole year 
    days_with_data_year = tropomi_mask.resample(date='Y').sum()
    
    return days_with_data_month, days_with_data_year

# running function 
days_with_data_month, days_with_data_year = Days_of_Data(tropomi_col_no2)

############################## Plotting Data #################################
# use spatial plotting functions from "plotting_functions.py"

# individual months
for month in range(12): 
    monthly_data = days_with_data_month[month, :, :]
    
    # date for plot title 
    date = days_with_data_month.date.values[month]
    full_date = str(date)
    year = full_date[0:4]
    
    pf.Spatial_Plotting_1ax(monthly_data, 0, 31,
                         (r'Number of days with data in '
                          +calendar.month_name[month+1]+', '+year), 
                         monthly_data.lon.values, 
                         monthly_data.lat.values, 
                         -126, 25, -60, 53, 
                         cm.get_cmap('Spectral_r', 30),
                         'Number of Days')
    
# full year 

# date for plot title 
date = days_with_data_year.date.values[0]
full_date = str(date)
year = full_date[0:4]

pf.Spatial_Plotting_1ax(days_with_data_year[0,:,:], 
                     0, 365,
                     (r'Number of days with data in '+year),  
                     days_with_data_year.lon.values, 
                     days_with_data_year.lat.values, 
                     -126, 25, -60, 53, 
                     cm.get_cmap('Spectral_r', 30),
                     'Number of Days')



################# Monthly and annual averages of variables ###################

def Temporal_Averages(tropomi_col_no2, geoscf_col_no2, 
                      geoscf_surf_no2, geoscf_temp):
    
    # taking monthly averages using resample 
    tropomi_col_no2_month = tropomi_col_no2.resample(
        date='M').mean()
    geoscf_col_no2_month = geoscf_col_no2.resample(
        date='M').mean()
    geoscf_surf_no2_month = geoscf_surf_no2.resample(
        date='M').mean()
    geoscf_temp_month = geoscf_temp.resample(
        date='M').mean()
    
    # yearly average using resample
    tropomi_col_no2_year = tropomi_col_no2.resample(
        date='Y').mean()
    geoscf_col_no2_year = geoscf_col_no2.resample(
        date='Y').mean()
    geoscf_surf_no2_year = geoscf_surf_no2.resample(
        date='Y').mean()
    geoscf_temp_year = geoscf_temp.resample(
        date='Y').mean()
    
    return (tropomi_col_no2_month, geoscf_col_no2_month, 
            geoscf_surf_no2_month, geoscf_temp_month, 
            tropomi_col_no2_year, geoscf_col_no2_year, 
            geoscf_surf_no2_year, geoscf_temp_year)

# using function to obtain averaged datasets 
(tropomi_col_no2_month_ave, geoscf_col_no2_month_ave, 
 geoscf_surf_no2_month_ave, geoscf_temp_month_ave, 
 tropomi_col_no2_year_ave, geoscf_col_no2_year_ave, 
 geoscf_surf_no2_year_ave, geoscf_temp_year_ave) = Temporal_Averages(
     tropomi_col_no2, geoscf_col_no2_masked, geoscf_surf_no2_masked, 
     geoscf_temp_masked)

# plotting monthly average column NO2
for month in range(12):
    # date for plot title 
    date = tropomi_col_no2_month_ave.date.values[month]
    full_date = str(date)
    year = full_date[0:4]
    
    pf.Spatial_Plotting_2ax(tropomi_col_no2_month_ave[month,:,:], 
                         'TROPOMI', 0, 2.5e16,
                         tropomi_col_no2_month_ave.lon.values, 
                         tropomi_col_no2_month_ave.lat.values,
                         cm.get_cmap('Spectral_r', 30),
                         r'Column NO$_2$',
                         geoscf_col_no2_month_ave[month,:,:], 
                         'GEOS-CF', 0, 2.5e16, 
                         geoscf_col_no2_month_ave.lon.values, 
                         geoscf_col_no2_month_ave.lat.values,
                         cm.get_cmap('Spectral_r', 30),
                         r'Column NO$_2$',
                         (r'Monthly Average Column NO$_2$ in ' 
                          +calendar.month_name[month+1]+', '+year),
                         -126, 25, -60, 53)
    
# plotting yearly average column NO2
pf.Spatial_Plotting_2ax(tropomi_col_no2_year_ave[0,:,:], 
                     'TROPOMI', 0, 2.5e16, 
                     tropomi_col_no2_year_ave.lon.values, 
                     tropomi_col_no2_year_ave.lat.values,
                     cm.get_cmap('Spectral_r', 30),
                     r'Column NO$_2$ (molecules/m$^2$)',
                     geoscf_col_no2_year_ave[0,:,:], 
                     'GEOS-CF', 0, 2.5e16, 
                     geoscf_col_no2_year_ave.lon.values, 
                     geoscf_col_no2_year_ave.lat.values,
                     cm.get_cmap('Spectral_r', 30),
                     r'Column NO$_2$ (molecules/m$^2$)',
                     (r'Average Column NO$_2$ in '+year),  
                     -126, 25, -60, 53)