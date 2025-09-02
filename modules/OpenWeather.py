from typing import Optional
import requests
from config import Config
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
class OpenWeatherAPI:
    def __init__(self, config: Config):
        self.config = config
        self.api_key = config.OPENWEATHER_API_KEY
        self.weather_api = config.OPENWEATHER_URL

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((
                requests.HTTPError,
                requests.ConnectionError,
                requests.Timeout,
                requests.RequestException
        ))
    )
    def get_weather_data_from_Open_Weather(self, city_geocode_data: dict) -> Optional[dict]:
        """
        Get weather data using geocoding response.

        Args:
            city_geocode_data: Dict from geocoding API like:
                      {'Krakow': {'lat': 50.061, 'lon': 19.936, 'name': 'Krakow', ...}}
        """
        try:
            if not city_geocode_data:
                raise ValueError("City data is empty")

            # Extract data directly
            city_key, city_info = next(iter(city_geocode_data.items()))

            lat = city_info['lat']
            lon = city_info['lon']
            city_name = city_info.get('name', city_key)
            country = city_info.get('country', 'Unknown')

            # Validate coordinates
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                raise ValueError(f"Invalid coordinates: lat={lat}, lon={lon}")

            # Build URL and make request
            url: str = self.weather_api.replace("{lat}", str(lat)) \
                .replace("{lon}", str(lon)) \
                .replace("{APIkey}", self.api_key)

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            print(f"Weather data retrieved for {city_name}, {country}")
            return response.json()

        except (KeyError, ValueError) as e:
            print(f"Data error: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    @staticmethod
    def kelvin_to_celsius(kelvin):
        """Convert temperature from Kelvin to Celsius"""
        return round(kelvin - 273.15,2)

    @staticmethod
    def format_time(timestamp):
        """Convert Unix timestamp to readable time"""
        return datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')

    def get_weather_data_from_dict(self,response_from_ow_data: dict):
        """Extract weather information from dictionary data"""

        # Validate input is a dictionary
        if not isinstance(response_from_ow_data, dict):
            raise TypeError(f"Expected dictionary, got {type(response_from_ow_data)}")

        try:
            # Safe extraction with proper error handling
            sys_data = response_from_ow_data.get('sys', {})
            weather_data = response_from_ow_data.get('weather', [{}])
            main_data = response_from_ow_data.get('main', {})

            # Extract location info
            country = sys_data.get('country', 'Unknown')
            city_name = response_from_ow_data.get('name', 'Unknown')

            # Extract weather info with safe access
            weather_info = weather_data[0] if weather_data else {}
            main_weather = weather_info.get('main', 'Unknown')
            description = weather_info.get('description', 'No description')

            # Extract temperature data with validation
            temp_raw = main_data.get('temp')
            feels_like_raw = main_data.get('feels_like')
            temp_min_raw = main_data.get('temp_min')
            temp_max_raw = main_data.get('temp_max')

            # Convert temperatures (only if values exist)
            temp = self.kelvin_to_celsius(temp_raw) if temp_raw is not None else None
            feels_like = self.kelvin_to_celsius(feels_like_raw) if feels_like_raw is not None else None
            temp_min = self.kelvin_to_celsius(temp_min_raw) if temp_min_raw is not None else None
            temp_max = self.kelvin_to_celsius(temp_max_raw) if temp_max_raw is not None else None

            # Extract other metrics (pressure should NOT be converted from Kelvin!)
            pressure = main_data.get('pressure')  # Already in hPa
            humidity = main_data.get('humidity')  # Already in %

            # Optional: Extract additional useful data
            visibility = response_from_ow_data.get('visibility')  # in meters
            wind_data = response_from_ow_data.get('wind', {})
            wind_speed = wind_data.get('speed')  # m/s
            wind_direction = wind_data.get('deg')  # degrees

            # Construct result dictionary
            result = {
                'location': f"{city_name}, {country}" if city_name != 'Unknown' else country,
                'weather': main_weather,
                'description': description,
                'temp': temp,
                'feels_like': feels_like,
                'temp_min': temp_min,
                'temp_max': temp_max,
                'pressure': pressure,
                'humidity': humidity,
                'visibility': visibility,
                'wind_speed': wind_speed,
                'wind_direction': wind_direction
            }

            return result

        except (KeyError, IndexError, AttributeError) as e:
            print(f"Error parsing weather data: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in parse_weather_data: {e}")
            return None


    def print_data(self, weather_data: dict):
        print(f'''Weather: {weather_data["weather"]} - {weather_data["description"]},
        Temperature: {weather_data["temp"]}C, feels like {weather_data["feels_like"]} C,
        Max temperature: {weather_data["temp_max"]} C,
        Min temperature: {weather_data["temp_min"]} C,
        Pressure: {weather_data["pressure"]} hPa,
        Visibility: {weather_data["visibility"]} m,
        Wind speed: {weather_data["wind_speed"]} m/s,
        Wind direction: {weather_data["wind_direction"]} deg
        ''')