import os
import pandas as pd
import pytest
import json


from src import ingest, transform, load

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")

def test_full_pipeline(tmp_path):
    # 1) ingest: carregar arquivo de exemplo
    infile = os.path.join(FIXTURES, "sample.json")
    raw_df = ingest.load_local_file(infile)
    assert not raw_df.empty

    # 2) transform: limpar dados
    transformed = transform.clean_data(raw_df)
    assert "rate" in transformed.columns
    assert (transformed["rate"] >= 0).all()

    # 3) load: salvar em parquet
    outfile = tmp_path / "out.parquet"
    load.save_to_parquet(transformed, outfile)
    assert outfile.exists()

    # reabre e valida
    df_check = pd.read_parquet(outfile)
    assert set(df_check.columns).issuperset({"currency", "rate"})
