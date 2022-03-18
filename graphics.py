from tkinter import *
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math, random, time, os
import matplotlib.tri as tri
import matplotlib.patches as patches
import convex_hull


class Graphics:
    def __init__(self, elevationData):
        self.elevationData = elevationData
        self.tk = Tk()
        self.tk.wm_title("WildfireSim")
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.canvas = None
        self.fire = None
        self.activeFire = {}
        self.burntPts = {}
        self.timeTracker = Label(self.tk, text="")
        self.timeTracker.pack(side=TOP)
        self.startTime = 0
        self.info = Label(self.tk, text="")
        self.info.pack(side=TOP)
        self.weather_forecast = None
        self.fireButton = None
        self.updateButton = None
        self.hours = 0

    def start(self, wf):
        self.weather_forecast=wf
        frame = Frame(self.tk, borderwidth=2)
        self.plotElevationData()
        frame.pack(fill=BOTH, expand=1)
        self.fireButton = Button(frame, text="Click to start fire", command=self.startFire)
        self.fireButton.pack(side=TOP)
        endButton = Button(frame, text="End Simulation", command=self.end)
        endButton.pack(side=BOTTOM)
        self.updateButton = Button(frame, text="")
        self.updateButton.pack(side=BOTTOM)
        self.tk.mainloop()

    def plotElevationData(self):

        plt.contourf(self.elevationData, cmap="viridis")
        plt.colorbar(label='Elevation above sea level [m]')
        plt.gca().set_aspect('equal', adjustable='box')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tk)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

    def changeBtnTxt(self):
        self.updateButton["text"] = "Click to calculate fire growth"
        self.updateButton["command"] = self.growFire
        self.tk.mainloop()

    def growFire(self):
        try:
            for hour, hourly_weather in enumerate(self.weather_forecast, start=self.hours):
                self.updateFire()
                self.growFireFront(hourly_weather)
                break
            self.hours+=1
            self.updateButton["command"] = self.growFire
            self.tk.mainloop()
        except:
            self.updateFire()
            self.updateButton.destroy()
            self.timeTracker.configure(text="The simulation is over!")
            self.tk.mainloop()

    def growFireFront(self, weather):
        self.fire.setWindVector(weather.windSpeed, weather.windDirection)
        next_area = []
        next_area_points = {}  # use dictionary for O(1) lookups
        for curr_point in self.fire.firePerimeter:
            fire_points = self.fire.calcGrowthFromPoint(curr_point)
            for point in fire_points:
                # if not already on fire and is outside of current perimeter
                if next_area_points.get(point.key()) is None and not self.fire.fireBounds.contains_point((point.x, point.y)):
                    self.activeFire[point.key()] = point
                    next_area_points[point.key()] = point  # add point to dictionary for curr iter
                    next_area.append(point)
                    x, y = int(point.x), int(point.y)
                    c = plt.Circle((x, y), 1, color="red")
                    self.ax.add_patch(c)
                    point.fire.burn()
        self.canvas.get_tk_widget().update_idletasks()
        self.canvas.draw()
        self.fire.firePerimeter = convex_hull.get_perimeter(next_area)  # finds new perimeter from all local perimeters
        self.fire.updateFireBounds()

    def updateFire(self):
        for point in self.activeFire:
            if self.burntPts.get(point) is None:
                if self.activeFire[point].fire.fireStatus.value == 3:
                    x, y = int(point.split(", ")[0]), int(point.split(", ")[1])
                    c = plt.Circle((x, y), 1, color="black")
                    self.burntPts[point] = 1
                    self.ax.add_patch(c)

    def startFire(self):
        for point in self.fire.fireArea.items():
            status = point[1]
            if status.fire.fireStatus.value == 2:
                x, y = int(point[0].split(", ")[0]), int(point[0].split(", ")[1])
                c = plt.Circle((x, y), 1, color="red")
                self.ax.add_patch(c)
                status.fire.burn()
                self.activeFire[point[0]] = status
        self.startTime = time.time()
        #self.fireButton["text"] = ""
        self.fireButton.destroy()
        self.activateHover()
        self.canvas.get_tk_widget().update_idletasks()
        self.canvas.draw()
        self.clock()
        self.changeBtnTxt()

    def activateHover(self):
        self.canvas.mpl_connect("motion_notify_event",
                lambda event: self.hover(event))


    def hover(self, event):
        if event.inaxes == self.ax:
            temp_str = str(int(event.xdata)) + ", " + str(int(event.ydata))
            if self.fire.fireArea.get(temp_str) is not None:
                if self.hours > 1:
                    self.info.config(text="The fire area is currently {} meters^2 after {} hours of growth".format(
                        len(self.fire.fireArea) * self.fire.xPointScale * self.fire.yPointScale,
                        self.hours))
                else:
                    self.info.config(text="The fire area is currently {} meters^2 after {} hour of growth".format(
                        len(self.fire.fireArea) * self.fire.xPointScale * self.fire.yPointScale,
                        self.hours))
            else:
                self.info.config(text="")


    def clock(self):
        seconds = time.time() - self.startTime
        seconds = seconds % (24 * 3600)
        hour = int(seconds // 3600)
        seconds %= 3600
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        self.timeTracker.configure(
            text="Simulation has been running for {} hours {} minutes and {} seconds".format(hour, minutes, seconds))
        self.timeTracker.after(30000, self.clock)

    def end(self):
        sys.exit()
