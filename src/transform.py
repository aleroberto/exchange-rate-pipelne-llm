import os
import pandas as pd
from datetime import datetime
from pathlib import Path
import argparse

# Diretórios
BASE_DIR = Path(__file__).parent.parent
SILVER_DIR = BASE_DIR / "data" / "silver"
os.makedirs(SILVER_DIR, exist_ok=True)

def transform_data(df: pd.DataFrame, date_str: str):
    """Aplica transformações e salva arquivo Silver"""
    
    # Aqui você aplica suas transformações normais no df
    # Exemplo fictício: arredondar taxas
    if "rate" in df.columns:
        df["rate_rounded"] = df["rate"].round(4)
    
    # Nome do arquivo Silver incluindo a data
    silver_file = SILVER_DIR / f"{date_str}.parquet"
    
    # Salva de forma idempotente
    df.to_parquet(silver_file, index=False)
    
    print(f"Silver file criado: {silver_file}")
    return silver_file

def main(date_str: str):
    # Aqui você carregaria o DataFrame de entrada (ex: ingest output)
    # Exemplo de DataFrame dummy
    df = pd.DataFrame({
        "date": [date_str],
        "base_currency": ["USD"],
        "target_currency": ["BRL"],
        "rate": [5.25],
        "retrieved_at": [datetime.utcnow().isoformat()]
    })
    
    transform_data(df, date_str)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transform script")
    parser.add_argument("--date", required=True, help="Data (YYYY-MM-DD)")
    args = parser.parse_args()
    
    main(args.date)
