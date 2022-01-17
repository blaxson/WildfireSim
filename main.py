import elevation
import weather
import os, sys
import matplotlib 
import matplotlib.pyplot as plt
import numpy as np

def main():
    if len(sys.argv) < 4:
        print("usage: python3 main.py DEM.tif latitude longitude")
        sys.exit(1)
    
    ''' elevation data '''
    filename = sys.argv[1]
    try:
        elevation_data = elevation.getDataFromFile(filename) # get elevation data from DEM
    except FileNotFoundError:
        print(f"{filename}: file not found")
        sys.exit(1)
    except elevation.FileNotSupportedError:
        print(f"{filename}: file not supported\n\tWildfireSim only supports .tif files")
        sys.exit(1)
    if elevation_data is None:
        print(f"{filename}: could not open image file")
        sys.exit(1)

    ''' weather data '''
    apikey = 'H2TfW0sqrQG96bRwsszmg2Hb6gEh61As'
    # latitude, longitude = 39.382558, 123.657235
    latitude, longitude = sys.argv[2], sys.argv[3]
    try:
        weather_data = weather.getWeatherData(apikey, latitude, longitude)
    except weather.WeatherAPIError as e:
        print(e.message)
        sys.exit(1)
    
    print(weather_data)

    # TODO: temporary plotting of elevation data
    # remove once graphics are stable
    
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