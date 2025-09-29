import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("EXCHANGE_API_KEY")
base_url = os.getenv("EXCHANGE_BASE_URL")

if not api_key or not base_url:
    raise ValueError("Erro ao ler EXCHANGE_API_KEY ou EXCHANGE_BASE_URL do .env")

endpoint = f"{base_url}/{api_key}/latest/USD"
response = requests.get(endpoint)

if response.status_code == 200:
    data = response.json()
    print("Cotação do USD em relacao a outras moedas:")
    for moeda, valor in data.get("conversion_rates", {}).items():
        print(f"{moeda}: {valor}")
else:
    print("Erro na requisicao:", response.status_code, response.text)
