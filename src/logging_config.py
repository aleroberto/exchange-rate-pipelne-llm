import structlog
import logging
from datetime import datetime
import os
import uuid

# Diretório de logs
LOG_DIR = os.path.join(os.path.dirname(__file__), "../logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, f"{datetime.utcnow().strftime('%Y-%m-%d')}.log")

# Configuração básica do logging
logging.basicConfig(
    format="%(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# Configuração do structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

def get_run_id():
    """Gera um run_id único para rastreabilidade"""
    return f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

def get_logger(run_id=None, service=None):
    """
    Retorna um logger estruturado JSON.
    :param run_id: identificador da execução
    :param service: nome do serviço/módulo
    """
    logger = structlog.get_logger()
    if run_id:
        logger = logger.bind(run_id=run_id)
    if service:
        logger = logger.bind(service=service)
    return logger

def log_metrics(logger, step_name, count, elapsed_seconds):
    """
    Emite métricas básicas do pipeline
    :param logger: logger estruturado
    :param step_name: nome da etapa (ingest, transform, load, llm)
    :param count: quantidade de registros processados
    :param elapsed_seconds: tempo de execução da etapa
    """
    logger.info(
        "metrics",
        step=step_name,
        processed=count,
        elapsed_seconds=round(elapsed_seconds, 4)
    )
