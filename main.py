import os
import time
from datetime import datetime
import structlog
from src import ingest, transform, load, llm_enrich
from src.logging_config import structlog

# Criar run_id para rastreabilidade
run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

logger = structlog.get_logger()

def main():
    start_time = time.time()
    logger.info("pipeline_start", service="pipeline", run_id=run_id)

    try:
        # ---------------------------
        # ETAPA 1: Ingestão
        # ---------------------------
        raw_file = ingest.fetch_exchange_rates(base_currency="USD")
        logger.info("ingest_complete", service="ingest", run_id=run_id, arquivo=raw_file)

        # ---------------------------
        # ETAPA 2: Transformação
        # ---------------------------
        silver_file = transform.transform_file(raw_file)
        logger.info("transform_complete", service="transform", run_id=run_id, arquivo=silver_file)

        # ---------------------------
        # ETAPA 3: Carga
        # ---------------------------
        gold_file = load.aggregate_silver_files()
        logger.info("load_complete", service="load", run_id=run_id, arquivo=gold_file)

        # ---------------------------
        # ETAPA 4: Enriquecimento LLM
        # ---------------------------
        import pandas as pd
        df = pd.read_parquet(silver_file)
        llm_summary = llm_enrich.enrich_with_llm(df, run_id, simulate_llm=True)

        logger.info("llm_enrichment_complete", service="llm", run_id=run_id, summary=llm_summary)

    except Exception as e:
        logger.error("pipeline_failed", service="pipeline", run_id=run_id, error=str(e))
        raise

    finally:
        end_time = time.time()
        elapsed = end_time - start_time
        logger.info(
            "pipeline_end",
            service="pipeline",
            run_id=run_id,
            elapsed_seconds=round(elapsed, 2)
        )

if __name__ == "__main__":
    main()
