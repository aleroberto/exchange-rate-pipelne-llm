import pandas as pd
from src import transform
from datetime import datetime
import json


def test_transform_file(tmp_path):
    # Criar arquivo JSON de exemplo
    test_file = tmp_path / "test.json"
    data = {
        "base_code": "USD",
        "conversion_rates": {"USD": 1.0, "EUR": 0.9, "JPY": None},
        "_metadata": {"timestamp": datetime.utcnow().isoformat(), "status_code": 200, "url": "fake_url"}
    }
    test_file.write_text(json.dumps(data))

    silver_file = transform.transform_file(str(test_file))
    df = pd.read_parquet(silver_file)

 
    assert "base_currency" in df.columns
    assert "target_currency" in df.columns
    assert df["rate"].notnull().all()
    assert (df["rate"] > 0).all()
    assert "JPY" not in df["target_currency"].values  # taxa nula removida
