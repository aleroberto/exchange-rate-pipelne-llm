import json
from datetime import datetime
from pathlib import Path

def save_llm_insights(insights: dict, base_path: str = "data/gold") -> str:
    """
    Salva insights do LLM em JSON no formato YYYY-MM-DD-insights.json
    Retorna o caminho do arquivo salvo.
    """
    Path(base_path).mkdir(parents=True, exist_ok=True)

    filename = f"{datetime.today().strftime('%Y-%m-%d')}-insights.json"
    filepath = Path(base_path) / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(insights, f, indent=2, ensure_ascii=False)

    return str(filepath)


if __name__ == "__main__":
    fake_insight = {
        "date": str(datetime.today().date()),
        "summary": "Mercado de câmbio apresentou forte volatilidade.",
        "top_risks": ["Inflação EUA", "Política monetária Brasil"],
        "source": "OpenAI GPT-4"
    }
    print("Arquivo salvo em:", save_llm_insights(fake_insight))
