import csv
import sys
import arcpy
from datetime import datetime, timezone, timedelta

from weather import is_delayed_weather_at_location


def get_airport_coords(airport_code: str):
    """Returns the coordinates (lat, lon) of the airport given the airport code."""

    with open("data/usa_airport_codes.csv", "r") as csvfile:
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

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 flight_delay.py <SOURCE_AIRPORT_CODE> <DESTINATION_AIRPORT_CODE>")
        quit()
    
    source_airport = sys.argv[1]
    destination_airport = sys.argv[2]

    print(f"Determining aircraft delays: {source_airport} --> {destination_airport}...")

    src_lat, src_lon = get_airport_coords(source_airport)
    dest_lat, dest_lon = get_airport_coords(destination_airport)

    if src_lat is None or dest_lat is None:
        print("Error: airport code not found")
        quit()
    
    # Find delays at source/departure airport
    departure_dt = datetime.now(tz=timezone.utc)
    delayed_departure = is_delayed_weather_at_location(src_lat, src_lon, departure_dt)

    geodesic_distance = airport_distance(src_lon, src_lat, dest_lon, dest_lat)
    hours = geodesic_distance/1000/800 #800 km/hr is the average plane speed

    print(geodesic_distance, hours)

    # Find delays at destination/arrival airport
    # TODO: vary the number of hours below based on the flight time between both points (I defaulted to 3)
    arrival_dt = datetime.now(tz=timezone.utc) + timedelta(hours=hours)
    delayed_arrival = is_delayed_weather_at_location(dest_lat, dest_lon, arrival_dt)

    print(f"Delayed departure: {delayed_departure}")
    print(f"Delayed arrival: {delayed_arrival}")


if __name__ == "__main__":
    main()
