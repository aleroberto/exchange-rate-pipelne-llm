# exchange-rate-pipelne-llm
Pipeline de cotações cambiais com Python, armazenamento em camadas (raw, silver, gold) e geração de insights com LLM.

## Estrutura inicial de diretórios

- /data/raw         → Dados brutos coletados da API de câmbio
- /data/silver      → Dados transformados e validados em formato parquet
- /data/gold        → Dados finais prontos para consumo analítico e relatórios

## Configuração de variáveis de ambiente

Para rodar este projeto, criar um arquivo `.env` com as variáveis:
EXCHANGE_API_KEY= (Preencher com a respectiva chave de API)
EXCHANGE_BASE_URL=(Preencher a URI corresondente)
OPENAI_API_KEY=(Preencher com a respectiva chave de API)
DB_URI=(Preencher a URI corresondente ao Banco)
ENV=dev (Preencher com DEV ou PROD)

