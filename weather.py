import requests
import datetime
import json
import numpy as np

''' custom error '''
class WeatherAPIError(Exception):
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return self.message

class Weather:
    def __init__(self, time, temperature, windSpeed, windDirection, windGust=None,
                 cloudCover=None, precProb=None, precInt=None, precType=None):
        self.time = time
        self.temperature = temperature
        self.windSpeed = windSpeed
        self.windGust = windGust
        self.windDirection = windDirection
        self.cloudCover = cloudCover
        self.precipitationProbability = precProb
        ''' maybe not needed? '''
        self.precipitationIntensity = precInt
        self.precipitationType = precType 
    
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"time: {self.time},\t temperature: {self.temperature:.2f},\t windSpeed: {self.windSpeed:.2f},\t " + \
               f"windGust: {self.windGust:.2f},\t windDirection: {self.windDirection:.2f},\t cloudCover: {self.cloudCover:.1f},\t " + \
               f"precipitationProbability: {self.precipitationProbability}"

''' gets the weather data of the given latitude and longitude coordinates, 
    returns np array of weather objects, where each index holds an hourly 
    weather forecast '''
def getWeatherData(apikey, latitude, longitude):
    # latitude ranges b/w -90 and 90, longitude b/w -180 and 180
    if latitude < -90 or latitude > 90 or longitude < -180 or longitude > 180:
        raise WeatherAPIError(f"latitude must be between -90 and 90 inclusive,\n" + \
                              f"longitude must be between -180 and 180 inclusive;" + \
                              f"given (lat, lon): {latitude}, {longitude}\n")

    weatherURL = "https://api.tomorrow.io/v4/timelines"

    querystring = {
    "location":f"{latitude}, {longitude}",
    "fields":["temperature", "windSpeed", "windGust", "windDirection", "cloudCover", 
            "precipitationType", "precipitationProbability", "precipitationIntensity"],
    "units":"imperial",
    "timesteps":"1h",
    "apikey":apikey
    }

    # make api request
    r = requests.request("GET", weatherURL, params=querystring)
    if r.status_code >= 400:
        raise WeatherAPIError(r.text)
    
    # convert response to json and get weather entries
    r_json = r.json()
    entries = r_json['data']['timelines'][0]['intervals']

    weather_points = []
    for entry in entries: # extract weather data from each entry
        time = entry['startTime']
        values = entry['values']
        weather = Weather(time=time, temperature=values['temperature'], windSpeed=values['windSpeed'], 
                          windDirection=values['windDirection'], windGust=values['windGust'],
                          cloudCover=values['cloudCover'], precProb=values['precipitationProbability'],
                          precInt=values['precipitationIntensity'], precType=values['precipitationType'])
        
        weather_points.append(weather)

    return np.asarray(weather_points)