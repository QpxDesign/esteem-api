import cdsapi
import os
from datetime import datetime, timedelta
import time

# cleanup
if os.path.exists("./src/gc_forecast/recent/latest.grib"):
    os.remove("./src/gc_forecast/recent/latest.grib")
if os.path.exists("./src/gc_forecast/recent/six_ago.grib"):
    os.remove("./src/gc_forecast/recent/latest.grib")
if os.path.exists("./src/gc_forecast/recent/latest.nc"):
    os.remove("./src/gc_forecast/recent/latest.nc")
if os.path.exists("./src/gc_forecast/recent/six_ago.nc"):
    os.remove("./src/gc_forecast/recent/latest.nc")

c = cdsapi.Client()

today = datetime.now()
five_days_ago = today - timedelta(days=6)

c.retrieve(
    'reanalysis-era5-pressure-levels',
    {
        'product_type': 'reanalysis',
        'format': 'grib',
        'variable': [
            'divergence', 'fraction_of_cloud_cover', 'geopotential',
            'ozone_mass_mixing_ratio', 'potential_vorticity', 'relative_humidity',
            'specific_cloud_ice_water_content', 'specific_cloud_liquid_water_content', 'specific_humidity',
            'specific_rain_water_content', 'specific_snow_water_content', 'temperature',
            'u_component_of_wind', 'v_component_of_wind', 'vertical_velocity',
            'vorticity',
        ],
        'pressure_level': [
            '1', '2', '3',
            '5', '7', '10',
            '20', '30', '50',
            '70', '100', '125',
            '150', '175', '200',
            '225', '250', '300',
            '350', '400', '450',
            '500', '550', '600',
            '650', '700', '750',
            '775', '800', '825',
            '850', '875', '900',
            '925', '950', '975',
            '1000',
        ],
        'year': five_days_ago.year,
        'month': five_days_ago.month,
        'day': five_days_ago.day,
        'time': f"{five_days_ago.hour}:00",
    },
    './src/gc_forecast/recent/latest.grib')
time.sleep(5)
five_days_six_hours_ago = five_days_ago - timedelta(hours=6)

c.retrieve(
    'reanalysis-era5-pressure-levels',
    {
        'product_type': 'reanalysis',
        'format': 'grib',
        'variable': [
            'divergence', 'fraction_of_cloud_cover', 'geopotential',
            'ozone_mass_mixing_ratio', 'potential_vorticity', 'relative_humidity',
            'specific_cloud_ice_water_content', 'specific_cloud_liquid_water_content', 'specific_humidity',
            'specific_rain_water_content', 'specific_snow_water_content', 'temperature',
            'u_component_of_wind', 'v_component_of_wind', 'vertical_velocity',
            'vorticity',
        ],
        'pressure_level': [
            '1', '2', '3',
            '5', '7', '10',
            '20', '30', '50',
            '70', '100', '125',
            '150', '175', '200',
            '225', '250', '300',
            '350', '400', '450',
            '500', '550', '600',
            '650', '700', '750',
            '775', '800', '825',
            '850', '875', '900',
            '925', '950', '975',
            '1000',
        ],
        'year': five_days_six_hours_ago.year,
        'month': five_days_six_hours_ago.month,
        'day': five_days_six_hours_ago.day,
        'time': f"{five_days_six_hours_ago.hour}:00",
    },
    './src/gc_forecast/recent/six_ago.grib')

os.system("grib_to_netcdf ./src/gc_forecast/recent/latest.grib -o ./src/gc_forecast/recent/latest.nc")
os.system("grib_to_netcdf ./src/gc_forecast/recent/six_ago.grib -o ./src/gc_forecast/recent/six_ago.nc")
