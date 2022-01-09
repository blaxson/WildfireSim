import elevation
import os, sys
import matplotlib 
import matplotlib.pyplot as plt
import numpy as np

def main():
    if len(sys.argv) < 2:
        print("usage: python3 main.py DEM.tif")
        sys.exit(1)
    
    filename = sys.argv[1]
    try:
        data = elevation.getDataFromFile(filename) # get elevation data from DEM
    except FileNotFoundError:
        print(f"{filename}: file not found")
        sys.exit(1)
    except elevation.FileNotSupportedError:
        print(f"{filename}: file not supported\n\tWildfireSim only supports .tif files")
        sys.exit(1)
    if data is None:
        print(f"{filename}: could not open image file")
        sys.exit(1)
    
    # TODO: temporary plotting of elevation data
    # remove once graphics are stable

    print(len(data))
    print(len(data[0]))
    print(data)
    fig = plt.figure(figsize = (12, 8))
    ax = fig.add_subplot(111)
    plt.contour(data, cmap = "viridis", 
                levels = list(range(0, 4500, 100)))
    plt.title("Elevation Contours of Mt. Whitney")
    cbar = plt.colorbar()
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

if __name__ == '__main__':
    main()