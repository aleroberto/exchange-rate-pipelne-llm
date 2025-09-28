import os
import json
from decimal import Decimal
import pandas as pd
from datetime import datetime
import structlog

logger = structlog.get_logger()
RAW_DIR = os.path.join(os.path.dirname(__file__), "../data/raw")
SILVER_DIR = os.path.join(os.path.dirname(__file__), "../data/silver")
REJECT_DIR = os.path.join(RAW_DIR, "rejects")
os.makedirs(SILVER_DIR, exist_ok=True)
os.makedirs(REJECT_DIR, exist_ok=True)

def transform_file(filepath, expected_base="USD"):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    rates = data.get("conversion_rates", {})
    retrieved_at = data["_metadata"]["timestamp"]
    base_currency = data.get("base_code", expected_base)
    date_str = datetime.utcnow().strftime("%Y-%m-%d")

    records = []
    rejects = []

    for target, rate in rates.items():
        try:
            if rate is None or rate <= 0:
                raise ValueError("Rate inválida")
            records.append({
                "base_currency": base_currency,
                "target_currency": target,
                "rate": round(float(rate), 6),
                "retrieved_at": retrieved_at,
                "date": date_str
            })
        except Exception as e:
            rejects.append({"target_currency": target, "rate": rate, "reason": str(e)})

    if rejects:
        reject_file = os.path.join(REJECT_DIR, f"{date_str}_rejects.json")
        with open(reject_file, "w", encoding="utf-8") as f:
            json.dump(rejects, f, ensure_ascii=False, indent=2)
        logger.error("transform_rejects", arquivo=reject_file, count=len(rejects))

    df = pd.DataFrame(records).drop_duplicates(subset=["target_currency", "retrieved_at"])
    silver_file = os.path.join(SILVER_DIR, f"{date_str}.parquet")
    df.to_parquet(silver_file, engine="pyarrow", compression="snappy", index=False)
    logger.info("transform_ok", arquivo=silver_file, count=len(df))
    return silver_file
