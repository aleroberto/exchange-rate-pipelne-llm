import os
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import structlog

logger = structlog.get_logger()

SILVER_DIR = os.path.join(os.path.dirname(__file__), "../data/silver")
GOLD_DIR = os.path.join(os.path.dirname(__file__), "../data/gold")
os.makedirs(GOLD_DIR, exist_ok=True)

DB_URI = os.getenv("DB_URI")

def aggregate_silver_files():
    files = [os.path.join(SILVER_DIR, f) for f in os.listdir(SILVER_DIR) if f.endswith(".parquet")]
    df_list = [pd.read_parquet(f) for f in files]
    df = pd.concat(df_list, ignore_index=True)
    df.drop_duplicates(subset=["date", "base_currency", "target_currency"], inplace=True)

    run_timestamp = datetime.utcnow().isoformat()
    run_id = run_timestamp.replace(":", "").replace("-", "").replace("T", "_")
    df.attrs["pipeline_version"] = "1.0"
    df.attrs["run_id"] = run_id
    df.attrs["run_timestamp"] = run_timestamp

    gold_file = os.path.join(GOLD_DIR, f"{run_id}.parquet")
    df.to_parquet(gold_file, engine="pyarrow", compression="snappy", index=False)
    logger.info("load_ok", arquivo=gold_file, count=len(df))


    if DB_URI:
        engine = create_engine(DB_URI)
        df.to_sql("exchange_rates", con=engine, if_exists="append", method="multi", index=False, chunksize=1000)
        logger.info("load_db_ok", table="exchange_rates", count=len(df))

    return gold_file
