# exchange-rate-pipelne-llm
Pipeline de cotações cambiais com Python, armazenamento em camadas (raw, silver, gold) e geração de insights com LLM.

## Estrutura inicial de diretórios

- /data/raw         → Dados brutos coletados da API de câmbio
- /data/silver      → Dados transformados e validados em formato parquet
- /data/gold        → Dados finais prontos para consumo analítico e relatórios
