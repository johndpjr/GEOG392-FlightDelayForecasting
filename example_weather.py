from datetime import datetime, timezone, timedelta

from weather import is_delayed_weather_at_location


# Departing from Houston Hobby (HOU)
hou_lat = "29.6407"
hou_lon = "-95.2740"

# Get the closest weather forecast for the departure airport
departure_dt = datetime.now(tz=timezone.utc)
delayed_departure = is_delayed_weather_at_location(hou_lat, hou_lon, departure_dt)

# Arriving at Denver International Airport (DEN)
den_lat = "39.849312"
den_lon = "-104.673828"

# Get the weather forecast for the arrival airport (assuming a 3 hr flight)
arrival_dt = datetime.now(tz=timezone.utc) + timedelta(hours=3)
delayed_arrival = is_delayed_weather_at_location(den_lat, den_lon, arrival_dt)

print(f"Delayed departure: {delayed_departure}")
print(f"Delayed arrival: {delayed_arrival}")
