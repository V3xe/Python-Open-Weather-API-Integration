import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()
@dataclass
class Config:
    #Openweather config
    OPENWEATHER_API_KEY: str = os.getenv('OPENWEATHER_API_KEY')
    OPENWEATHER_URL: str = os.getenv('OPENWEATHER_URL')
    #Geocoding config
    GEOCODING_URL: str = os.getenv('GEOCODING_URL')

    #Retries