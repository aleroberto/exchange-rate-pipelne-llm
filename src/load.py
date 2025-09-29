import os
import time
import pandas as pd
import sqlite3
from sqlalchemy import create_engine
from datetime import datetime
from pathlib import Path
from src.logging_config import get_logger, log_metrics
from sqlalchemy import text

SILVER_DIR = os.path.join(os.path.dirname(__file__), "../data/silver")
GOLD_DIR = os.path.join(os.path.dirname(__file__), "../data/gold")
os.makedirs(GOLD_DIR, exist_ok=True)

DB_URI = os.getenv("DB_URI")

def aggregate_silver_files(run_id=None, date_str=None):
    logger = get_logger(run_id=run_id, service="load")
    start = time.time()

    if not date_str:
        date_str = datetime.utcnow().strftime("%Y-%m-%d")

    # Filtra arquivos Silver do dia específico
    files = [os.path.join(SILVER_DIR, f) for f in os.listdir(SILVER_DIR) if f.endswith(".parquet") and date_str in f]
    if not files:
        logger.warning("no_silver_files", date=date_str)
        return None

    # Lê e concatena
    df_list = [pd.read_parquet(f) for f in files]
    df = pd.concat(df_list, ignore_index=True)
    df.drop_duplicates(subset=["date", "base_currency", "target_currency"], inplace=True)

    # --- SALVA GOLD PARQUET (idempotente) ---
    gold_file = os.path.join(GOLD_DIR, f"{date_str}.parquet")
    df.to_parquet(gold_file, engine="pyarrow", compression="snappy", index=False)
    logger.info("load_ok", arquivo=gold_file, count=len(df))

    # Log de métricas
    elapsed = time.time() - start
    log_metrics(logger, "load", df.shape[0], elapsed)

    # --- SALVA NO BANCO (idempotente) ---
    if DB_URI:
        engine = create_engine(DB_URI)
        with engine.connect() as conn:
            # Remove registros do mesmo dia antes de inserir
            conn.execute(text("DELETE FROM exchange_rates WHERE date = :date"), {"date": date_str})

        df.to_sql("exchange_rates", con=engine, if_exists="append", method="multi", index=False, chunksize=1000)
        logger.info("load_db_ok", table="exchange_rates", count=len(df))

    return gold_file

def save_to_parquet(df: pd.DataFrame, outfile: str | Path):
    """Salva DataFrame em arquivo parquet"""
    df.to_parquet(outfile, index=False)

def save_to_sqlite(df: pd.DataFrame, dbfile: str | Path, table_name: str, date_str=None):
    """Salva DataFrame em banco SQLite de forma idempotente"""
    conn = sqlite3.connect(dbfile)
    cursor = conn.cursor()

    if date_str:
        # Remove registros do mesmo dia
        cursor.execute(f"DELETE FROM {table_name} WHERE date = ?", (date_str,))
        conn.commit()

    df.to_sql(table_name, conn, if_exists="append", index=False)
    conn.close()

def main(date_str=None):
    gold_file = aggregate_silver_files(date_str=date_str)
    if gold_file:
        print(f"Gold file criado: {gold_file}")
    else:
        print(f"Nenhum arquivo Silver encontrado para {date_str}")

if __name__ == "__main__":
    main()
