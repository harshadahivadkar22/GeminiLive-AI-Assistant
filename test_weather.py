import os
from dotenv import load_dotenv
import requests

load_dotenv()
api_key = os.environ.get("WEATHER_API_KEY")
print("Key:", api_key)

url = f"http://api.openweathermap.org/data/2.5/weather?q=Pune&appid={api_key}&units=metric"
response = requests.get(url)
print("Status:", response.status_code)
print("Data:", response.text)
