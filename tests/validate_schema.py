import pandas as pd
import os


gold_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data/gold")
files = [f for f in os.listdir(gold_dir) if f.endswith(".parquet")]
if not files:
    raise FileNotFoundError("Nenhum arquivo .parquet encontrado em /data/gold")

latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(gold_dir, f)))
filepath = os.path.join(gold_dir, latest_file)

print(f"Validando schema do arquivo: {filepath}")

# Lê o parquet
df = pd.read_parquet(filepath)


expected_cols = {
    "date": "object",              # pode vir como string ou datetime64
    "base_currency": "object",
    "target_currency": "object",
    "rate": "float64",
    "retrieved_at": "int64",       # pode variar dependendo do ingest (timestamp)
    "run_id": "object",
    "pipeline_version": "object"
}

# Verificação
ok = True
for col, expected_type in expected_cols.items():
    if col not in df.columns:
        print(f" Coluna ausente: {col}")
        ok = False
    else:
        actual_type = str(df[col].dtype)
        if actual_type != expected_type:
            print(f"Coluna {col}: esperado {expected_type}, encontrado {actual_type}")
        else:
            print(f"Coluna {col}: {actual_type}")

if ok:
    print("\nSchema válido! Arquivo pronto para entrega.")
else:
    print("\nCorrija o schema antes da entrega.")
