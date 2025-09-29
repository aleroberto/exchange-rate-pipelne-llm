import os
import json
from src.llm_insights import save_llm_insights

def test_save_llm_insights(tmp_path):
    # Mock de dados simulando resposta do LLM
    insights = {
        "date": "2025-09-29",
        "summary": "Teste de geração de insights.",
        "top_risks": ["Risco cambial", "Inflação global"],
        "source": "Mock LLM"
    }

    # Salva insights no diretório temporário
    filepath = save_llm_insights(insights, base_path=tmp_path)

    # Verifica se o arquivo foi criado
    assert os.path.exists(filepath)

    # Carrega de volta e valida
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["summary"] == "Teste de geração de insights."
    assert "top_risks" in data
    assert data["source"] == "Mock LLM"
