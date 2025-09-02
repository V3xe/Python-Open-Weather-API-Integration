from modules.Geocoding import Geocoding
from modules.OpenWeather import OpenWeatherAPI
from config import Config
import requests

def main():

    #Get city name in EN, lat and lon for further processing

    geocoding: Geocoding = Geocoding(Config())
    try:
        #Fetch data from geocoding API
        city = input("City to fetch weather data for: ")
        city_geocode_data: dict = geocoding.get_city_data(city)
        print(f"City data: {city_geocode_data}")
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            print("City not found. Please check the spelling.")
        elif e.response.status_code == 401:
            print("Invalid API key. Please check your configuration.")
        else:
            print(f"API error: {e}")
    except (requests.ConnectionError, requests.Timeout):
        print("Network error. Please check your internet connection.")
    except Exception as e:
        print(f"Unexpected error: {e}")

    weather_data: OpenWeatherAPI = OpenWeatherAPI(Config())
    response: dict = weather_data.get_weather_data_from_Open_Weather(city_geocode_data)
    weather_data_parsed: dict = weather_data.get_weather_data_from_dict(response)
    weather_data.print_data(weather_data_parsed)



if __name__ == '__main__':
    main()