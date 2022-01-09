from osgeo import gdal, osr
from osgeo.gdalconst import GA_ReadOnly

class FileNotSupportedError(Exception):
    pass

''' takes in the filename of a tif as a string, returns elevation matrix '''
def getDataFromFile(filename):
    gdal.AllRegister()
    gdal.UseExceptions()

    # Open Image
    try:
        ras_data = gdal.Open(filename, GA_ReadOnly)
    except (FileNotFoundError, RuntimeError) as e: # convert gdal's RuntimeError to FileNotFoundError
        errorString = str(e)
        if "No such file or directory" in errorString:
            raise FileNotFoundError
        if "not recognized as a supported file format" in errorString:
            raise FileNotSupportedError
        raise e
    if ras_data is None:
        return None

    # read in the raster data and get elevation matrix from it
    band1 = ras_data.GetRasterBand(1)
    rows = ras_data.RasterYSize
    cols = ras_data.RasterXSize
    elevationData = band1.ReadAsArray(0,0,cols,rows)

    # TODO: still need to format elevation data
    return elevationData

    '''
    other useful attributes:
        elevationData.shape
        elevationData.size
        numrows = len(elevationData)
        numcols = len(elevationData[0])
    '''
    