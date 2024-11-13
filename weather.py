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
    """Returns if the airport's weather forecast indicates a potentially delayed flight at the specified dt moment."""

    # Retrieve the weather at the location
    weather = _get_weather_at_location(lat, lon)
    # Get the closest forecast to the time point
    forecast = _get_closest_forecast(weather, dt)
    return _is_delayable_weather(forecast)
