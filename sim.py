import convex_hull # local module
import numpy as np
import enum
import random # temporary
import math
from matplotlib.path import Path

''' represents a single point on map; includes all data necessary (excluding weather) 
    needed for fire growth calculations, and all data needed for graphics driver '''
class MapPoint:
    def __init__(self, elevation, xPos, yPos):
        self.elevation = np.short(elevation) # convert to numpy types to save memory
        self.x = xPos
        self.y = yPos
        ''' don't need 3D slope, can calculate fire growth 
            to all surrounding points given their elevation (calc. relative slope)
            i.e find slope between 5-5, 8-5, 9-5, 4-5, 7-5, 3-5, 5-5, 8-5
               5  8  9
                \ | /
               4<-5->7
                / | \ 
               3  5  8
        '''
        self.fire = FirePoint() # pulled into own class for optimizations in fire calculations
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return f"(x: {self.x}, y: {self.y}, el: {self.elevation}, {self.fire})"
    def key(self): # unique identifier for point
        return f"{self.x}, {self.y}"

''' represents the data necessary to perform fire calculations '''
class FirePoint: 
    def __init__(self):
        self.fuelType = np.ubyte(1) # const fuel source # TODO: provide opportunity for future work
        self.fireStatus = FireStatus.unburnt # for graphics purposes
        self.timeRemaining = np.ushort(0) # time remaining of fire in hours, only applicable if fireStatus = active
        '''
        Fuels are classified by diameter as follows:
        (less than 0.25in)   1-hour fuel
        (0.25-1in)           10-hour fuel
        (1-3in)              100-hour fuel
        (3-8in)              1000 hour fuel
        ''' 
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return f"fuel: {self.fuelType}, status: {self.fireStatus}, remaining: {self.timeRemaining}h"

    # TODO: consider creating a static hash map / dictionary to store all these values for faster lookups 
    #       in future work involving expanding fuel types
    def fuelMoisture(self):
        if self.fuelType == 1:
            return 0.40
    def bulkDensity(self):
        if self.fuelType == 1:
            return 0.03
    def particleDensity(self):
        if self.fuelType == 1:
            return 30
    def packingRatio(self):
        return self.bulkDensity() / self.particleDensity()
    def relativePackingRatio(self):
        if self.fuelType == 1:
            return 0.23 # relative packing ratio for grass (avg. between short and long grass)
        elif self.fuelType == 2: # our implementation won't reach
            return 0.33 # relative packing ratio for avg. brush
        elif self.fuelType == 3:
            return 2.35 # relative packing ratio for timber litter 
        elif self.fuelType == 4:
            return None # cannot find
    ''' surface area to volume ratio '''
    def SAV(self):
        if self.fuelType == 1:
            return 2000 # relative SAV ratio for grass (avg. between short and long)
        elif self.fuelType == 2: # our implementation won't reach
            return 350 # relative SAV ratio for brush
        elif self.fuelType == 3:
            return 2000 # relative SAV ratio for timber litter 
        elif self.fuelType == 4:
            return None # cannot find
    def effectiveHeatingNumber(self):
        return math.exp(-138/self.SAV())
    
    ''' changes fireStatus from unburnt to active and sets the timeRemaining
        to be the correct time given the fuel type '''
    def ignite(self):
        # don't do anything if area already burned or is already on fire
        if self.fireStatus != FireStatus.unburnt:
            return
        self.fireStatus = FireStatus.active
        if self.fuelType == 1:
            self.timeRemaining = 1 
        elif self.fuelType == 2:
            self.timeRemaining = 10
        elif self.fuelType == 3:
            self.timeRemaining = 100
        elif self.fuelType == 4:
            self.timeRemaining = 1000
    
    ''' decrements the time remaining by one hour, changes fireStatus to burnt 
        if timeRemaining reaches zero '''
    def burn(self):
        self.timeRemaining = self.timeRemaining - 1
        if self.timeRemaining <= 0:
            self.fireStatus = FireStatus.burnt

class FireStatus(enum.Enum):
    unburnt = 1
    active = 2
    burnt = 3     

class Simulator:
    def __init__(self, mapPoints, xScale, yScale):
        self.map = mapPoints
        self.yBoundary, self.xBoundary = mapPoints.shape
        # 1 point on map = 1 pointScale meters 
        # i.e if pointScale = 10, then the distance b/w two adjacent points on map = 10 meters
        self.xPointScale = xScale 
        self.yPointScale = yScale
        self.windVector = None # gets set after each iteration of growFire()
        self.firePerimeter = [] 
        self.fireBounds = None
        self.fireArea = {} # all points that have caught fire, dictionary for lookup performance
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return f"width: {self.xBoundary}, height: {self.yBoundary}, " + \
               f"xScale: {self.xPointScale}, yScale: {self.yPointScale}, map:\n{self.map}"

    def setWindVector(self, windSpeed, windDirection):
        s = windSpeed * 5280 / 60 # convert windSpeed from mph to feet/min
        self.windVector = calculateWindVector(s, windDirection)
    def isOutOfBounds(self, point):
        if point.x < 0 or point.y < 0:
            return True 
        if point.x > self.xBoundary or point.y > self.yBoundary:
            return True
        return False   
    
    ''' converts distance in meters to distance in map indeces '''
    def xMetersToPoints(self, meters):
        return meters // self.xPointScale
    def yMetersToPoints(self, meters):
        return meters // self.yPointScale
    ''' returns the physical distance between two points, in meters '''
    def distanceBetweenPoints(self, p1, p2):
        x = abs(p2.x - p1.x) * self.xPointScale
        y = abs(p2.y - p1.y) * self.yPointScale
        return math.sqrt(x*x + y*y)
    ''' returns a vector in component form (in feet) for two ponts, where p1 is origin and p2 is end of vector '''
    def vectorize(self, p1, p2):
        x = (p2.x - p1.x) * self.xPointScale * 3.28084 # 3.28084 feet per meter
        y = (p2.y - p1.y) * self.yPointScale * 3.28084
        return np.array([x, y])
    ''' updates the fire bounds with a new Path, given the current firePerimeter '''
    def updateFireBounds(self):
        bounds = []
        for point in self.firePerimeter:
            bounds.append((point.x, point.y))
        self.fireBounds = Path(bounds, closed=True)

    ''' starts a fire with radius of size size (meters) at dX, dY position as a percentage on map '''
    def startFire(self, xPercent, yPercent, size):
        xPos = int(self.xBoundary * xPercent)
        yPos = int(self.yBoundary * yPercent)

        xStart = xPos - self.xMetersToPoints(size)
        xEnd = xPos + self.xMetersToPoints(size)
        yStart = yPos - self.yMetersToPoints(size)
        yEnd = yPos + self.yMetersToPoints(size)
        
        # ensure boundaries are accounted for
        xStart = 0 if xStart < 0 else int(xStart)
        xEnd = self.xBoundary if xEnd > self.xBoundary else int(xEnd)
        yStart = 0 if yStart < 0 else int(yStart)
        yEnd = self.yBoundary if yEnd > self.yBoundary else int(yEnd)

        bounds = []
        # ignite each point in calculated region and add to active fire queue
        for y in range(yStart, yEnd):
            for x in range(xStart, xEnd):
                point = self.map[y, x]
                point.fire.ignite() # TODO: add graphics update here
                bounds.append(point)
                if self.fireArea.get(point.key()) is None:
                    self.fireArea[point.key()] = point
        self.firePerimeter = convex_hull.get_perimeter(bounds)
        self.updateFireBounds()

    ''' returns Rothermel's slope factor for surface fire spread. S = 5.275 * P^(-0.3)*(tanTheta)^2 '''
    def slopeFactor(self, p1, p2): # guarenteed to be different p1 and p2
        packingRatio = p1.fire.packingRatio()
        # tan theta = dY / dX, where dY is change in elevation, dX is distance between points
        tanTheta = (p2.elevation - p1.elevation) / self.distanceBetweenPoints(p1, p2)
        return 5.275 * (packingRatio ** -0.3) * (tanTheta * tanTheta) # Rothermel's slope factor

    ''' returns Rothermel's wind factor for surface fire spread 
        note: Rothermel's model goes into great depth on calculating the effective flamespeed given
        several more environmental factors, so this approach is simplified. '''
    def windFactor(self, p1, p2): # guarenteed to be different p1 and p2
        sv = p1.fire.SAV()
        C = 7.47 * math.exp(-0.133 * (sv ** 0.55))
        B = 0.02526 * (sv ** 0.54)
        E = -1 * (0.715 * math.exp(-3.59 * 0.0001 * sv))

        # calculate wind speed in given direction of two points
        v = self.vectorize(p1, p2)
        vectorScalar = self.windVector.dot(v) / v.dot(v) # (u dot v / v dot v) v
        localWindVector = v * vectorScalar
        localWindSpeed = np.sqrt(localWindVector.dot(localWindVector)) # vector's magnitude
        res = C * (localWindSpeed ** B) * (p1.fire.relativePackingRatio() ** E) # Rothermel's wind factor (units are feet/min)
        return 0 if vectorScalar < 0 else res # disregard windfactor if it is in hurting direction

    ''' returns Rothermel's propagating flux ratio '''
    def propagatingFlux(self, point):
        sv = point.fire.SAV()
        p = point.fire.packingRatio()
        return ((192 + 0.2595 * sv) ** -1) * (math.exp((0.792 + 0.681 * (sv ** 0.5)) * (p * 0.1)))
    
    def reactionIntensity(self):
        return 3000 # was common reaction intensity given 0.20-0.30 packing ratio
        
    ''' returns entire numerator to Rothermel's fire spread calculation '''
    def heatSource(self, p1, p2):
        return self.reactionIntensity() * self.propagatingFlux(p1) * (1 + self.windFactor(p1, p2) + self.slopeFactor(p1, p2))
    
    ''' returns entire denominator to Rothermel's fire spread calculation 
        input is the point in prospect to catch fire '''
    def heatSink(self, point):
        Q = 250 + 1116 * point.fire.fuelMoisture() # heat of preignition
        return point.fire.bulkDensity() * point.fire.effectiveHeatingNumber() * Q
    
    ''' returns the rate of spread (in meters / hours) for fire in the direction of p1 -> p2 '''
    def rateOfSpread(self, p1, p2):
        rate = self.heatSource(p1, p2) / self.heatSink(p2)
        # convert rate from feet/min to meters/hr
        return rate * 60 / 3.28084

    ''' given a single point, calculates all the points around it that the fire will spread to;
        excludes points that are already burnt,
        ignites points that have not been burned yet '''
    def calcGrowthFromPoint(self, point):
        nRate = neRate = eRate = seRate = 0
        sRate = swRate = wRate = nwRate = 0
        # get rate of spread in each direction
        if point.y - 1 >= 0:
            nRate = self.rateOfSpread(point, self.map[point.y-1, point.x])
            if point.x - 1 >= 0:
                nwRate = self.rateOfSpread(point, self.map[point.y-1, point.x-1])
            if point.x + 1 < self.xBoundary:
                neRate = self.rateOfSpread(point, self.map[point.y-1, point.x+1])
        if point.y + 1 < self.yBoundary:
            sRate = self.rateOfSpread(point, self.map[point.y+1, point.x])
            if point.x - 1 >= 0:
                swRate = self.rateOfSpread(point, self.map[point.y+1, point.x-1])
            if point.x + 1 < self.xBoundary:
                seRate = self.rateOfSpread(point, self.map[point.y+1, point.x+1])
        if point.x - 1 >= 0:
            wRate = self.rateOfSpread(point, self.map[point.y, point.x-1])
        if point.x + 1 < self.xBoundary:
            eRate = self.rateOfSpread(point, self.map[point.y, point.x+1])
        
        # calculate coordinates for perimeter points
        # North
        y = point.y - self.yMetersToPoints(nRate)
        nX = point.x
        nY = 0 if y < 0 else int(y)
        
        # Northeast
        dX, dY = getXYFireSpread(neRate)
        x = point.x + self.xMetersToPoints(dX)
        y = point.y - self.yMetersToPoints(dY)
        neX = self.xBoundary if x > self.xBoundary else int(x)
        neY = 0 if y < 0 else int(y)
       
        # East
        x = point.x + self.xMetersToPoints(eRate)
        eX = self.xBoundary if x > self.xBoundary else int(x)
        eY = point.y

        # Southeast
        dX, dY = getXYFireSpread(seRate)
        x = point.x + self.xMetersToPoints(dX)
        y = point.y + self.yMetersToPoints(dY)
        seX = self.xBoundary if x > self.xBoundary else int(x)
        seY = self.yBoundary if y > self.yBoundary else int(y)

        # South 
        y = point.y + self.yMetersToPoints(sRate)
        sX = point.x
        sY = self.yBoundary if y > self.yBoundary else int(y)

        # Southwest
        dX, dY = getXYFireSpread(swRate)
        x = point.x - self.xMetersToPoints(dX)
        y = point.y + self.yMetersToPoints(dY)
        swX = 0 if x < 0 else int(x)
        swY = self.yBoundary if y > self.yBoundary else int(y)

        # West
        x = point.x - self.xMetersToPoints(wRate)
        wX = 0 if x < 0 else int(x)
        wY = point.y

        # Northwest
        dX, dY = getXYFireSpread(nwRate)
        x = point.x - self.xMetersToPoints(dX)
        y = point.y - self.yMetersToPoints(dY)
        nwX = 0 if x < 0 else int(x)
        nwY = 0 if y < 0 else int(y)

        fireBoundary = [(nX, nY), (neX, neY), (eX, eY), (seX, seY), 
                        (sX, sY), (swX, swY), (wX, wY), (nwX, nwY)]
        fire = Path(fireBoundary, closed=True)

        # calculate rectangle overlay of fire polygon; narrows points to parse through
        minY = min(nwY, nY, neY) # most northern point
        maxY = max(seY, sY, swY) # most southern point
        minX = min(nwX, wX, swX) # most western point
        maxX = max(neX, eX, seX) # most eastern point

        points = []
        for y in range(minY, maxY):
            for x in range(minX, maxX):
                p = (x, y)
                point = self.map[y, x]
                # if point is in bounds of spread and is not already burnt, ignite and add to points
                if fire.contains_point(p) and point.fire.fireStatus != FireStatus.burnt:
                    points.append(point)
                    # add point to fireArea if not alread in it
                    if self.fireArea.get(point.key()) is None:
                        self.fireArea[point.key()] = point
                    point.fire.ignite() # ignite fire if not already burnt # TODO: add graphics update here
        return points
    
    ''' runs single iteration of fire growth, equivalent to one hour of growth;
        works by iterating through every point in the active fire front (firePerimeter),
        and creating a new queue for next iteration of fireFront'''
    def growFireFront(self, weather):
        self.setWindVector(weather.windSpeed, weather.windDirection)
        next_area = []
        next_area_points = {} # use dictionary for O(1) lookups
        for curr_point in self.firePerimeter:
            fire_points = self.calcGrowthFromPoint(curr_point)
            for point in fire_points:
                # if not already on fire and is outside of current perimeter
                if next_area_points.get(point.key()) is None and not self.fireBounds.contains_point((point.x, point.y)):
                    next_area_points[point.key()] = point # add point to dictionary for curr iter
                    next_area.append(point)
        self.firePerimeter = convex_hull.get_perimeter(next_area) # finds new perimeter from all local perimeters
        self.updateFireBounds()

    ''' TODO: no longer used '''
    ''' runs single iteration of fire growth, equivalent to one hour of growth;
        works by iterating through every point in the active fire queue,
        and creating a new queue for next iteration '''
    def growFire(self, weather):
        self.setWindVector(weather.windSpeed, weather.windDirection)
        next_iteration = []
        next_iteration_points = {} # use dictionary for O(1) lookups
        while len(self.firePerimeter) > 0:
            curr_point = self.firePerimeter.pop(0)
            # decrement time remaining for current point in fire queue
            curr_point.fire.burn()
            # if fire still burning at point, add back to queue
            if curr_point.fire.timeRemaining > 0:
                # ensure not already in queue from any previous call to calcGrowthFromPoint()
                if next_iteration_points.get(point.key()) is None:
                    next_iteration_points[curr_point.key()] = curr_point
                    next_iteration.append(curr_point)
            surrounding_points = self.calcGrowthFromPoint(curr_point)
            ''' TODO: only add points to fireQueue if they are perimeter points, 
            but stxill ensure all points are being ignited and burned '''
            for point in surrounding_points:
                # ensure not already in queue from any previous call to calcGrowthFromPoint()
                if next_iteration_points.get(point.key()) is None:
                    point.fire.ignite()
                    next_iteration_points[point.key()] = point # add point to dictionary for current iter
                    next_iteration.append(point)
        
        # next_iteration becomes new firePerimeter
        self.firePerimeter = convex_hull.get_perimeter(next_iteration)

''' gets the wind vector as a numpy vector given wind speed and direction '''
def calculateWindVector(speed, direction):
    x, y = calculateVectorComponents(speed, direction)
    return np.array([x, y])

''' gets the x and y coordinates of fire spread given rate of spread along the diagonal '''
def getXYFireSpread(rate):
    x, y = calculateVectorComponents(rate, 45)
    return x, y

def calculateVectorComponents(magnitude, direction):
    x = magnitude * math.cos(math.radians(direction))
    y = magnitude * math.sin(math.radians(direction))
    return x, y