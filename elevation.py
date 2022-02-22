from osgeo import gdal, osr
from osgeo.gdalconst import GA_ReadOnly

''' custom error '''
class FileNotSupportedError(Exception):
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return self.message

''' takes in the filename of a tif as a string, returns the map distance of each pixel and elevation matrix '''
def getElevationData(filename):
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
            raise FileNotSupportedError("file not supported\n\tWildfireSim only supports .tif files")
        raise e
    if ras_data is None:
        return None
    
    # get DEM metadata
    info = ras_data.GetGeoTransform()
    spatial = ras_data.GetSpatialRef()
    projected = bool(spatial.IsProjected())
    # dX represents the change in meters for 1 change in pixel in the x direction
    dX = info[1]
    # dY represents the change in meters for 1 change in pixel in the y direction
    dY = info[-1]
    # if the pixel size is not 1 or 10 meters or if the DEM is not projected to UTM
    if dX not in [1.0, 5.0, 10.0] and not projected:
        raise FileNotSupportedError("file not supported\n\tDEM should be in UTM coordinate format (meters)")
 
    # read in the raster data and get elevation matrix from it
    band1 = ras_data.GetRasterBand(1)
    rows = ras_data.RasterYSize
    cols = ras_data.RasterXSize
    elevationData = band1.ReadAsArray(0,0,cols,rows)

    return abs(dX), abs(dY), elevationData

    '''
    other useful attributes:
        elevationData.shape
        elevationData.size
        numrows = len(elevationData)
        numcols = len(elevationData[0])
    '''
    