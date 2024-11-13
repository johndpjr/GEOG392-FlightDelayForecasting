import csv
from datetime import datetime, timezone, timedelta
import sys

from weather import is_delayed_weather_at_location


def get_airport_coords(airport_code: str) -> tuple[float, float]:
    """Returns the coordinates (lat, lon) of the airport given the airport code."""

    with open("data/usa_airport_codes.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["iata"] == airport_code:
                return (str(row["latitude"]), str(row["longitude"]))
    return (None, None)  # airport code not found


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

    # Find delays at destination/arrival airport
    # TODO: vary the number of hours below based on the flight time between both points (I defaulted to 3)
    arrival_dt = datetime.now(tz=timezone.utc) + timedelta(hours=3)
    delayed_arrival = is_delayed_weather_at_location(dest_lat, dest_lon, arrival_dt)

    print(f"Delayed departure: {delayed_departure}")
    print(f"Delayed arrival: {delayed_arrival}")


if __name__ == "__main__":
    main()
