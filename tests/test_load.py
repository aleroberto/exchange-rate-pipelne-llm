import os
import sqlite3
import pandas as pd
import pytest

from src import load

def test_save_to_parquet(tmp_path):
    # cria dataframe de exemplo
    df = pd.DataFrame({"currency": ["USD", "EUR"], "rate": [5.0, 6.0]})
    outfile = tmp_path / "test.parquet"

    # executa função
    load.save_to_parquet(df, outfile)

    # valida se arquivo existe
    assert outfile.exists()

    # valida conteúdo
    loaded = pd.read_parquet(outfile)
    assert list(loaded.columns) == ["currency", "rate"]
    assert loaded.shape == (2, 2)


def test_save_to_sqlite(tmp_path):
    # cria dataframe de exemplo
    df = pd.DataFrame({"currency": ["USD", "EUR"], "rate": [5.0, 6.0]})
    dbfile = tmp_path / "test.db"

    # executa função
    load.save_to_sqlite(df, dbfile, "exchange_rates")

    # conecta no SQLite e valida
    conn = sqlite3.connect(dbfile)
    rows = conn.execute("SELECT * FROM exchange_rates").fetchall()
    conn.close()

    assert len(rows) == 2
    assert rows[0][0] in ("USD", "EUR")
