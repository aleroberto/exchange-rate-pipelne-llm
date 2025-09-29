import os
import json
import pytest
from src import ingest

def test_fetch_exchange_rates(monkeypatch, tmp_path):
    # Monkeypatch requests.get para simular resposta HTTP
    class MockResponse:
        status_code = 200
        def json(self):
            return {"conversion_rates": {"USD": 1.0, "EUR": 0.9}}

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr("requests.get", mock_get)

    filepath = ingest.fetch_exchange_rates(base_currency="USD")
    assert os.path.exists(filepath)

    with open(filepath, "r") as f:
        data = json.load(f)
    assert "conversion_rates" in data
    assert "_metadata" in data
