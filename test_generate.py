import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

data = {
    "contents": [{"parts": [{"text": "Hola"}]}]
}

response = requests.post(url, json=data)
print(f"Status: {response.status_code}")
print(response.json())