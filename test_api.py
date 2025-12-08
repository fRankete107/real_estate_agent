import requests
import os
from dotenv import load_dotenv

load_dotenv("real_estate_agent/.env")
api_key = os.getenv("GOOGLE_API_KEY")

print(f"Key termina en: ...{api_key[-6:]}")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
response = requests.get(url)

if response.status_code == 200:
    models = response.json().get("models", [])
    print("\nModelos disponibles:")
    for m in models:
        print(f"  - {m['name']}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)