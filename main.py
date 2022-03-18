import elevation, weather, sim, convex_hull# local modules
import sys
import numpy as np
from graphics import Graphics

def printError(msg):
    print("WildfireSim: " + msg, file=sys.stderr)

""" used for printing progress of data initialization, params include:
    iteration  : current iteration (Int)
    total      : total iterations (Int)
    fill       : bar fill character (Str)
    printEnd   : end character (e.g. "\r", "\r\n") (Str)
"""
def printProgressBar (iteration, total, fill='█', printEnd="\r"):
    percent = ("{0:." + str(1) + "f}").format(100 * (iteration / float(total)))
    length = 50 # char length of bar
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\rLoading Map Data: |{bar}| {percent}% Complete', end = printEnd)
    # Print newline on complete
    if iteration == total: 
        print()

''' retrieves weather data from weather module and handles all errors '''
def getWeatherData(latStr, lonStr):
    # get environment variable
    #apikey = os.getenv('WEATHER_ACCESS')
    apikey = "bTwTZqRIM3x7mrUWKUr3lR1uVCPupCor";
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
    printProgressBar(0, y)
    for i_y in range(0, y):
        line = []
        for i_x in range(0, x):
            point = sim.MapPoint(elevation_data[i_y, i_x], i_x, i_y)
            line.append(point)
        mapPoints.append(line)
        printProgressBar(i_y + 1, y)

    # TODO: temporarily returns elevation_data (for matplot)
    return np.asarray(mapPoints), dX, dY, elevation_data

''' formats the fire starting location and its size '''
def getFireStart(xStr, yStr, rStr):
    try:
        xPercent = float(xStr)
        yPercent = float(yStr)
        radius = int(rStr)
        if radius <= 0:
            raise ValueError
    except ValueError:
        printError("xPercent, yPercent must be float between 0.0 - 1.0,\n" + \
                    "size must be a positive integer")
        sys.exit(1)
    return xPercent, yPercent, radius

def main():
    if len(sys.argv) < 7:
        print("usage: python3 main.py DEM.tif latitude longitude, xPercent, yPercent, size")
        print("\twhere xPercent, yPercent = 0.0-1.0 representing the location of fire start on map")
        print("\tand size is size of fire's radius in meters")
        sys.exit(1)
    xPercent, yPercent, radius = getFireStart(sys.argv[4], sys.argv[5], sys.argv[6])
    weather_forecast = getWeatherData(sys.argv[2], sys.argv[3])
    mapPoints, dX, dY, elevation_data = getMapData(sys.argv[1]) # TODO: remove elevation_data from return val

    fireSim = sim.Simulator(mapPoints, dX, dY)
    fireSim.startFire(xPercent, yPercent, radius)
    graph = Graphics(elevation_data)
    graph.fire = fireSim
    graph.start(weather_forecast)

if __name__ == '__main__':
    main()