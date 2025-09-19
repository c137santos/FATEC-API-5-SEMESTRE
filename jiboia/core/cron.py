import logging
from datetime import datetime
from .service.jira_svc import JiraService

logger = logging.getLogger(__name__)

def jira_healthcheck():
    """
    Função executada pelo cron para fazer o healthcheck da API do Jira.
    Esta função é chamada pelo django-crontab de acordo com o agendamento configurado
    no settings.py. Ela registra o resultado em logs e pode ser expandida para
    enviar alertas em caso de falha.
    """
    start_time = datetime.now()
    logger.info(f"[CRON] Iniciando healthcheck da API do Jira em {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    success, message = JiraService.healthcheck()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    if success:
        logger.info(f"[CRON] Healthcheck da API do Jira concluído com sucesso em {duration:.2f}s: {message}")
    else:
        logger.error(f"[CRON] Healthcheck da API do Jira falhou após {duration:.2f}s: {message}")
    
    return success