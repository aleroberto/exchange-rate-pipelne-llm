import os
import json
import time
import pandas as pd
from datetime import datetime
from src.logging_config import get_logger, log_metrics

RAW_DIR = os.path.join(os.path.dirname(__file__), "../data/raw")
SILVER_DIR = os.path.join(os.path.dirname(__file__), "../data/silver")
REJECT_DIR = os.path.join(RAW_DIR, "rejects")
os.makedirs(SILVER_DIR, exist_ok=True)
os.makedirs(REJECT_DIR, exist_ok=True)

def transform_file(filepath, run_id=None, expected_base="USD"):
    logger = get_logger(run_id=run_id, service="transform")
    logger.info("transform_start", arquivo=filepath)
    start = time.time()

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

    elapsed = time.time() - start
    log_metrics(logger, "transform", df.shape[0], elapsed)

    return silver_file

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Remove taxas nulas ou negativas e garante colunas essenciais."""
    if df.empty:
        return df
    df = df.dropna(subset=["rate"])
    df = df[df["rate"] > 0]
    expected_cols = ["base_currency", "target_currency", "rate"]
    return df[expected_cols].reset_index(drop=True)

def main(date_str=None):
    if not date_str:
        date_str = datetime.utcnow().strftime("%Y-%m-%d")

    raw_file = os.path.join(RAW_DIR, f"{date_str}.json")
    if not os.path.exists(raw_file):
        print(f"Arquivo RAW não encontrado: {raw_file}")
        return

    silver_file = transform_file(raw_file)
    print(f"Arquivo SILVER gerado: {silver_file}")

