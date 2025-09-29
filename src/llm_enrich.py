import os
import json
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import structlog
from dotenv import load_dotenv
from decimal import Decimal
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

logger = structlog.get_logger()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

LOG_FILE = os.path.join(os.path.dirname(__file__), "../logs/llm_prompts.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log_prompt(prompt, run_id):
    """Loga prompt e metadados para auditoria"""
    prompt_hash = hashlib.md5(prompt.encode("utf-8")).hexdigest()
    timestamp = datetime.utcnow().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "run_id": run_id,
        "prompt_hash": prompt_hash,
        "prompt": prompt
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

def calculate_metrics(df, N=30):
    """Calcula pct_change, volatilidade e top movers"""
    df['date'] = pd.to_datetime(df['date'])
    df.sort_values(by=['target_currency', 'date'], inplace=True)
    
    last_date = df['date'].max()
    current = df[df['date'] == last_date][['target_currency', 'rate']].set_index('target_currency')

    month_ago = last_date - pd.DateOffset(months=1)
    past_month_data = df[(df['date'] >= month_ago.replace(day=1)) & 
                         (df['date'] <= month_ago.replace(day=28))]
    past_avg = past_month_data.groupby('target_currency')['rate'].mean()

    pct_change = ((current['rate'] - past_avg) / past_avg * 100).fillna(0)

    volatility = df.groupby('target_currency').apply(
        lambda x: x.sort_values('date').tail(N)['rate'].pct_change().std() * 100
    )

    metrics = pd.DataFrame({
        'current_price': current['rate'],
        'pct_change': pct_change,
        'volatility': volatility
    }).reset_index()

    top_movers = metrics.reindex(metrics['pct_change'].abs().sort_values(ascending=False).index).head(5)
    
    return top_movers

def generate_llm_prompt(top_movers):
    """Gera prompt formatado para o LLM"""
    summary_json = top_movers.to_dict(orient='records')
    prompt = (
        f"Você é um analista financeiro. Receba estes dados agregados em JSON: {json.dumps(summary_json)} "
        "e gere um resumo executivo curto (3 frases) orientado a negócios, 3 insights acionáveis e um alerta se "
        "volatilidade > limiar. Explique comparando com o mês passado e cite percentuais."
    )
    return prompt

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_llm(prompt, run_id):
    """Chama a API do LLM e retorna resposta, com retry"""
    log_prompt(prompt, run_id)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )
    text = response.choices[0].message.content.strip()

    if not text:
        prompt_reduced = prompt[:2000]
        return call_llm(prompt_reduced, run_id)
    
    return text

def enrich_with_llm(df, run_id, simulate_llm=True):
    """
    Função principal para calcular métricas e gerar insights do LLM.
    Se simulate_llm=True, retorna resposta fake para desenvolvimento.
    """
    top_movers = calculate_metrics(df)
    
    if simulate_llm:
        # Retorno fake durante desenvolvimento
        llm_response = (
            "Resumo executivo simulado: "
            "1) Moeda X subiu 2% em relação ao mês passado; "
            "2) Moeda Y teve volatilidade alta; "
            "3) Atenção para a moeda Z com tendência de queda."
        )
        logger.info(
            "llm_enrichment_fake", 
            run_id=run_id, 
            top_movers=list(top_movers['target_currency'])
        )
        return llm_response
    
    # Código real para chamar o LLM
    prompt = generate_llm_prompt(top_movers)
    llm_response = call_llm(prompt, run_id)
    logger.info("llm_enrichment_ok", run_id=run_id, top_movers=list(top_movers['target_currency']))
    return llm_response
