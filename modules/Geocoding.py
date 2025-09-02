import requests
from config import Config
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class Geocoding:
    #Pass config: Config to get access to values from Config @dataclass and .env
    def __init__(self, config: Config):
        self.config = config
        self.geocode_url = config.GEOCODING_URL
        self.api_key = config.OPENWEATHER_API_KEY

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
    def get_city_data(self, city: str) -> dict:#List[Dict[str, Any]]:
        """
        Get geocoding data for a city.
        Returns the dictionary made from response or raises an exception after all retries fail.
        """
        try:
            url = self.geocode_url.replace('{City}', city).replace('{APIkey}', self.api_key)

            response = requests.get(url, timeout=10)
            response.raise_for_status()  # This raises HTTPError for 4xx/5xx status codes

            data = response.json()
            location_dict = {item['name']: item for item in data}
            return location_dict

        except requests.exceptions.RequestException as e:
            raise #re-raise the exception for tenacity to catch
