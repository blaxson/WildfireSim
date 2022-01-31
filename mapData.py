import numpy as np
import enum
import random # temporary

''' represents a single point on map; includes all data necessary (excluding weather) 
    needed for fire growth calculations, and all data needed for graphics driver '''
class MapPoint:
    def __init__(self, elevation):
        self.elevation = np.short(elevation) # convert to numpy types to save memory
        ''' don't need 3D slope, can calculate fire growth 
            to all surrounding points given their elevation (calc. relative slope)
            i.e find slope between 5-5, 8-5, 9-5, 4-5, 7-5, 3-5, 5-5, 8-5
               5  8  9
                \ | /
               4<-5->7
                / | \ 
               3  5  8
        '''
        self.fuelType = np.ubyte(1) # const fuel source, provide opportunity for future work
        self.fireStatus = FireStatus.unburnt # for graphics purposes
        self.timeRemaining = np.ushort(0) # time remaining of fire in hours, only applicable if fireStatus = active
        # self.currentBurnIntensity = 0 # needed?

    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return f"({self.elevation}, {self.fuelType}, {self.fireStatus}, {self.timeRemaining})"

class FireStatus(enum.Enum):
    unburnt = 1
    active = 2
    burnt = 3
