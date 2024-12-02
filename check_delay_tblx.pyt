# -*- coding: utf-8 -*-

import arcpy


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [Tool]


class Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Flight Delay Detector"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        departure_airport = arcpy.Parameter(
            displayName="What airport are you leaving from?",
            name="departure_airport",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
    
        arrival_airport = arcpy.Parameter(
            displayName="What airport are you going to?",
            name="arrival_airport",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        departure_time = arcpy.Parameter(
            displayName="What time does your flight leave?",
            name="departure_time",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
    
        params = [departure_airport, arrival_airport, departure_time]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        from datetime import datetime, timezone
        import requests
        import json


        API_KEY = "189b9f73b01fded31fef00424010e0d6"
        WIND_SPEED_THRESHOLD = 34  # mph
        METERS_PER_MILE = 1609
        DAYTIME_VISIBILITY_THRESHOLD = METERS_PER_MILE * 3  # meters
        NIGHTTIME_VISIBILITY_THRESHOLD = METERS_PER_MILE * 5  # meters
        POOR_WEATHER_CODES = [
            200,  # thunderstorm with light rain
            201,  # thunderstorm with rain
            202,  # thunderstorm with heavy rain
            210,  # light thunderstorm
            211,  # thunderstorm
            212,  # heavy thunderstorm
            221,  # ragged thunderstorm
            230,  # thunderstorm with light drizzle
            231,  # thunderstorm with drizzle
            232,  # thunderstorm with heavy drizzle
            # 500,  # light rain
            # 501,  # moderate rain
            502,  # heavy intensity rain
            503,  # very heavy rain
            504,  # extreme rain
            511,  # freezing rain
            # 520,  # light intensity shower rain
            # 521,  # shower rain
            522,  # heavy intensity shower rain
            # 531,  # ragged shower rain
            # 600,  # light snow
            # 601,  # snow
            602,  # heavy snow
            611,  # sleet
            # 612,  # light shower sleet
            # 613,  # shower sleet
            # 615,  # light rain and snow
            # 616,  # rain and snow
            # 620,  # light shower snow
            # 621,  # shower snow
            # 622,  # heavy shower snow
            701,  # mist
            711,  # smoke
            721,  # haze
            731,  # sand/dust whirls
            741,  # fog
            751,  # sand
            761,  # dust
            762,  # volcanic ash
            771,  # squalls
            781,  # tornado
        ]


        def _get_weather_at_location(lat: str, lon: str, units="imperial"):
            """Returns the OpenWeatherMap 5-day forcast (in 3 hr increments)."""

            url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units={units}"

            try:
                resp = requests.get(url)
                resp.raise_for_status()
            except requests.HTTPError as e:
                print(e.response.text)
                return None

            return json.loads(resp.text)


        def _get_closest_forecast(weather: dict, dt: datetime):
            """Returns the closest forecast to the datetime specified."""

            closest_forecast_index = 0
            min_forecast_distance = 60 * 60 * 24  # set to a large number
            for index, forecast in enumerate(weather["list"]):
                forecast_distance = abs((datetime.fromtimestamp(forecast["dt"], tz=timezone.utc) - dt).total_seconds())
                if forecast_distance < min_forecast_distance:
                    min_forecast_distance = forecast_distance
                    closest_forecast_index = index

            return weather["list"][closest_forecast_index]


        def _is_delayable_weather(forecast: dict) -> bool:
            """Returns if the weather forecast would cause a flight delay.
            Considers thunderstorms, wind speed, visibility, etc.
            """

            pod = forecast["sys"]["pod"]  # part of the day
            visi = forecast["visibility"]  # meters
            weather_codes = [weather["id"] for weather in forecast["weather"]]

            delayable_conditions = [
                forecast["wind"]["speed"] > WIND_SPEED_THRESHOLD,
                ((pod == "d" and visi < DAYTIME_VISIBILITY_THRESHOLD) or
                (pod == "n" and visi < NIGHTTIME_VISIBILITY_THRESHOLD)),
                any(code in POOR_WEATHER_CODES for code in weather_codes)
            ]

            if any(delayable_conditions):
                return True
            return False


        def is_delayed_weather_at_location(lat: str, lon: str, dt: datetime) -> bool:
            """Returns if the airport's weather forecast indicates a potentially delayed flight at the specified moment."""

            # Retrieve the weather at the location
            weather = _get_weather_at_location(lat, lon)
            # Get the closest forecast to the time point
            forecast = _get_closest_forecast(weather, dt)
            return _is_delayable_weather(forecast)
        
        import csv
        import sys
        import arcpy
        from datetime import datetime, timezone, timedelta

        def get_airport_coords(airport_code: str):
            """Returns the coordinates (lat, lon) of the airport given the airport code."""

            with open("C:\\Users\\Brown\\Downloads\\data\\usa_airport_codes.csv", "r") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row["iata"] == airport_code:
                        return (str(row["latitude"]), str(row["longitude"]))
            return (None, None)  # airport code not found



        def airport_distance(lon1, lat1, lon2, lat2):
            # Define the spatial reference (WGS 1984 is a common choice for geographic coordinates)
            spatial_ref = arcpy.SpatialReference(4326)  # EPSG code for WGS 1984

            # Define the two points (longitude, latitude)
            point1 = arcpy.Point(lon1, lat1)  # Example: Los Angeles International Airport
            point2 = arcpy.Point(lon2, lat2)   # Example: John F. Kennedy International Airport

            # Create point geometries
            point_geom1 = arcpy.PointGeometry(point1, spatial_ref)
            point_geom2 = arcpy.PointGeometry(point2, spatial_ref)

            # Calculate the geodesic distance (returns distance in meters by default)
            angle, geodesic_distance = point_geom1.angleAndDistanceTo(point_geom2, "GEODESIC")
            
            return geodesic_distance

        source_airport = parameters[0].valueAsText
        destination_airport = parameters[1].valueAsText

        arcpy.AddMessage(f"Determining aircraft delays: {source_airport} --> {destination_airport}...")

        src_lat, src_lon = get_airport_coords(source_airport)
        dest_lat, dest_lon = get_airport_coords(destination_airport)

        if src_lat is None or dest_lat is None:
            arcpy.AddError("Error: airport code not found")
            quit()
        
        # Find delays at source/departure airport
        departure_dt = datetime.now(tz=timezone.utc)
        delayed_departure = is_delayed_weather_at_location(src_lat, src_lon, departure_dt)

        geodesic_distance = airport_distance(src_lon, src_lat, dest_lon, dest_lat)
        hours = geodesic_distance/1000/800 #800 km/hr is the average plane speed


        # Find delays at destination/arrival airport
        arrival_dt = datetime.now(tz=timezone.utc) + timedelta(hours=hours)
        delayed_arrival = is_delayed_weather_at_location(dest_lat, dest_lon, arrival_dt)

        arcpy.AddMessage(f"Delayed departure: {delayed_departure}")
        arcpy.AddMessage(f"Delayed arrival: {delayed_arrival}")
        
        return

    def postExecute(self, parameters):
        arcpy.AddMessage("Execution Complete")
        return "test"
