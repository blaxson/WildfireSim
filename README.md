# WildfireSim
Senior Project that simulates the possibilities of a wild fire spreading

## Background Info:
- 3 factors that primarily affect a wildfire
  - Topography
  - Weather 
  - Fuel
  - (https://www.nps.gov/articles/wildland-fire-behavior.htm)

## Steps to run
1. WildfireSim uses tomorrow.io API to retrieve its weather data for its fire calculations. 
In order to run WildfireSim, set the environment variable 'WEATHER_ACCESS' 
with your correct API access key. ```$ export WEATHER_ACCESS=your_key```
More information can be found at https://docs.tomorrow.io/reference/api-authentication.
2. Retrieve a DEM.tif of your desired location from any source you wish. 
https://.... is a good starting point
3. Ensure all dependencies are installed on host
4. run ```$ python3 main.py DEM.tif latitude longitude xPercent yPercent radius``` with your DEM file,
the latitude and longitude of the DEM's central location, the starting position of the fire, 
and the fire's radius size in meters

# Dependencies
## To install gdal on linux
```
sudo apt-get install gdal-bin proj-bin libgdal-dev libproj-dev
```

## To install gdal on mac
```
brew install gdal 
pip3 install --upgrade pip
pip3 install gdal  
```

## Other library dependencies
```
pip3 install requests
```