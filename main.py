import elevation, weather, mapData # local modules
import os, sys
import matplotlib 
import matplotlib.pyplot as plt
import numpy as np
import random

def printError(*msg):
    print(*msg, file=sys.stderr)

''' retrieves weather data from weather module and handles all errors '''
def getWeatherData(latStr, lonStr):
    os.environ['WEATHER_ACCESS'] = 'H2TfW0sqrQG96bRwsszmg2Hb6gEh61As' # TODO: remove setting env var 
    # get environment variable
    apikey = os.getenv('WEATHER_ACCESS')
    if apikey is None:
        printError("must set 'WEATHER_ACCESS' environment variable with API access key")
        sys.exit(1)
    # latitude, longitude = 39.382558, 123.657235 
    try:
        lat = float(latStr)
        lon = float(lonStr)
        weather_data = weather.getWeatherData(apikey, lat, lon)
    except weather.WeatherAPIError as e:
        printError(e.message)
        sys.exit(1)
    except ValueError:
        printError("latitude and longitude must be of type float")
        sys.exit(1)
    return weather_data

''' retrieves elevation data from module, converts to map data and handles all errors '''
def getMapData(mapFile):
    ''' get elevation data '''
    try:
        dX, dY, elevation_data = elevation.getElevationData(mapFile) # get elevation data from DEM
    except FileNotFoundError:
        printError(f"{mapFile}: file not found")
        sys.exit(1)
    except elevation.FileNotSupportedError as e:
        printError(f"{mapFile}: {e.message}")
        sys.exit(1)
    if elevation_data is None:
        printError(f"{mapFile}: could not open image file")
        sys.exit(1)

    ''' convert elevation data into map data '''
    simMap = []
    for elevation_line in elevation_data:
        for elevation_point in elevation_line:
            point = mapData.MapPoint(elevation_point)
            simMap.append(point)
    # TODO: temporarily returns elevation_data (for matplot)
    return np.asarray(simMap), dX, dY, elevation_data

def main():
    if len(sys.argv) < 4:
        print("usage: python3 main.py DEM.tif latitude longitude")
        # TODO: uncomment sys.exit(1)
    
    weather_data = getWeatherData(sys.argv[2], sys.argv[3])
    simMap, dX, dY, elevation_data = getMapData(sys.argv[1])
    print(simMap)

    # TODO: temporary plotting of elevation data
    # remove once graphics are stable
    print(dX)
    print(dY)
    print(len(elevation_data))
    print(len(elevation_data[0]))
    print(elevation_data)
    fig = plt.figure(figsize = (12, 8))
    ax = fig.add_subplot(111)
    plt.contour(elevation_data, cmap = "viridis", 
                levels = list(range(0, 4500, 100)))
    plt.title("Elevation Contours of Mt. Whitney")
    cbar = plt.colorbar()
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

if __name__ == '__main__':
    main()