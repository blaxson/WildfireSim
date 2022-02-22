import elevation, weather, sim # local modules
import os, sys
import matplotlib 
import matplotlib.pyplot as plt
import numpy as np
import random
import time

def printError(msg):
    print("WildfireSim: " + msg, file=sys.stderr)

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

''' retrieves elevation data from module, converts to map data and handles all errors 
    returns np array of map'''
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

    y, x = elevation_data.shape
    ''' convert elevation data into map data '''
    mapPoints = []
    for i_y in range(0, y):
        line = []
        for i_x in range(0, x):
            point = sim.MapPoint(elevation_data[i_y, i_x], i_x, i_y)
            line.append(point)
        mapPoints.append(line)

    # TODO: temporarily returns elevation_data (for matplot)
    return np.asarray(mapPoints), dX, dY, elevation_data

def main():
    if len(sys.argv) < 4:
        print("usage: python3 main.py DEM.tif latitude longitude")
        # TODO: uncomment sys.exit(1)
    
    #weather_data = getWeatherData(sys.argv[2], sys.argv[3])
    #for data in weather_data:
    #    print(f"{data.windSpeed}, \t{data.windDirection}")
    
    start = time.time()
    mapPoints, dX, dY, elevation_data = getMapData(sys.argv[1])
    print(mapPoints.shape)
    end = time.time()
    print(f"took {end-start} seconds to getMapData")

    start = time.time()
    fireSim = sim.Simulator(mapPoints, dX, dY)
    fireSim.startFire(.25, .25, 10)
    print(f"\npoints in fire queue: {len(fireSim.fireQueue)}")
    print([(point.x, point.y) for point in fireSim.fireQueue])
    end = time.time()
    print(f"took {end-start} seconds to start fire")

    print(dX, dY)
    print()
    weather_data = []
    weather_data.append(weather.Weather("0", 54, 10, 193))

    start = time.time()
    fireSim.growFire(weather_data[0])
    print(f"\npoints in fire queue: {len(fireSim.fireQueue)}")
    print([(point.x, point.y) for point in fireSim.fireQueue])
    end = time.time()
    print(f"took {end-start} seconds to run first iteration")

    start = time.time()
    fireSim.growFire(weather_data[0])
    print(f"\npoints in fire queue: {len(fireSim.fireQueue)}")
    print([(point.x, point.y) for point in fireSim.fireQueue])
    end = time.time()
    print(f"took {end-start} seconds to run second iteration")


    start = time.time()
    fireSim.growFire(weather_data[0])
    print(f"\npoints in fire queue: {len(fireSim.fireQueue)}")
    print([(point.x, point.y) for point in fireSim.fireQueue])
    end = time.time()
    print(f"took {end-start} seconds to run third iteration")


    '''
    # TODO: temporary plotting of elevation data
    # remove once graphics are stable
    print(elevation_data)
    fig = plt.figure(figsize = (12, 8))
    ax = fig.add_subplot(111)
    plt.contour(elevation_data, cmap = "viridis", 
                levels = list(range(0, 4500, 100)))
    plt.title("Elevation Contours of Mt. Whitney")
    cbar = plt.colorbar()
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()
    '''

if __name__ == '__main__':
    main()