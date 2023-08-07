# PhD Research Repository
# Nitrogen Dioxide Variability over CONUS 

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Description

Welcome to my PhD research repository! Here you will find the code used for data processing and analysis in my research into modes of variability in nitrogen dioxide (NO2) over a variety of spatial and temporal scales across the contiguous United States. This research utilizes a variety of NO2 datasets, including the GEOS-CF model and TROPOMI satellite, to fill gaps in our understanding of this prevalent pollutant. The goal of this repository is to increase the accessibility and transparency of my research.

## Table of Contents
- [Description](#description)
- [Table of Contents](#table-of-contents)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
- [Research Projects](#research-projects)
- [Contributors](#contributors)
- [License](#license)
- [Contact Information](#contact-information)

## Getting Started

Datasets used are: 
- GEOS-CF model output for NO2, temperature, and pressure 
- GEOS-Chem NO2 emissions 
- TROPOMI satellite tropospheric column NO2 
- Shapefiles of United States, Canada, and Mexico political boundaries 
- United States land cover data from the NLCD

### Prerequisites

Code is written in Python 3.6.13. 
Necessary packages are numpy, xarray, Pandas, GeoPandas, Matplotlib, Basemap, datetime, calendar, pickle, os, osgeo, netCDF4, and rasterio. 

## Research Projects

### Project 1: Nitrogen Dioxide Correlations with Temperature 

Little research has been conducted examining nitrogen dioxide’s correlations with temperature. Previous studies examining this effect in agricultural areas have found there is likely a positive correlation when soil is the main NOx source. Almost no studies have examined this correlation in urban areas, a topic which is becoming increasingly important to understand as cities grow and global temperatures rise. The findings from this project will add to the body of research on temperature-NO2 correlations in agricultural environments plus will yield novel findings regarding temperature-NO2 correlations in urban and non-agricultural areas. 


### Project 2: Nitrogen Dioxide Seasonal Trends by Region 

We still lack a comprehensive understanding of NO2 seasonality in the United States. Previous studies have investigated NO2 seasonality and have found that it varies significantly by region and NO2 source. This project will utilize satellite and model tropospheric column NO2 data to discern NO2 seasonality in each region of the United States. Furthermore, disagreements between the model and satellite data will help pinpoint potential problems with these data sources and will be used to improve the model and satellite retrieval’s accuracy. 

## Contributors

This work is supervised by Dr. Jeffrey Geddes at Boston University. 

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

## Contact

If you have any questions, comments, or suggestions you can reach me at: 
- Email: rhmooers@bu.edu
