import os
import json
from datetime import datetime
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
import structlog

load_dotenv()
logger = structlog.get_logger()

API_KEY = os.getenv("EXCHANGE_API_KEY")
BASE_URL = os.getenv("EXCHANGE_BASE_URL")
RAW_DIR = os.path.join(os.path.dirname(__file__), "../data/raw")
os.makedirs(RAW_DIR, exist_ok=True)

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=30))
def fetch_exchange_rates(base_currency="USD"):
    url = f"{BASE_URL}/{API_KEY}/latest/{base_currency}"
    try:
        response = requests.get(url, timeout=10)
        timestamp = datetime.utcnow().isoformat()
        metadata = {
            "timestamp": timestamp,
            "status_code": response.status_code,
            "url": url
        }
        if response.status_code == 200:
            data = response.json()
            data["_metadata"] = metadata

            now = datetime.utcnow()
            filename = now.strftime("%Y-%m-%d.json")
            filepath = os.path.join(RAW_DIR, filename)
            if os.path.exists(filepath):
                filename = now.strftime("%Y-%m-%d_%H%M%S.json")
                filepath = os.path.join(RAW_DIR, filename)

            tmp_filepath = filepath + ".tmp"
            with open(tmp_filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_filepath, filepath)

            logger.info("fetch_ok", service="ingest", arquivo=filepath)
            return filepath
        else:
            logger.error("fetch_failed", service="ingest", status=response.status_code, url=url)
            response.raise_for_status()
    except requests.RequestException as e:
        logger.error("fetch_exception", service="ingest", error=str(e))
        raise

def load_local_file(filepath: str):
    """Carrega um arquivo JSON local de câmbio em DataFrame"""
    import pandas as pd

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return pd.DataFrame(data)
    elif isinstance(data, dict) and "conversion_rates" in data:
        rates = data["conversion_rates"]
        return pd.DataFrame(
            [{"currency": k, "rate": v} for k, v in rates.items()]
        )
    else:
        raise ValueError("Formato de arquivo não suportado")
