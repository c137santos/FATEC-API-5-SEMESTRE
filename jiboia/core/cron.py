import logging
from datetime import datetime

from jiboia.core.models import Project
from jiboia.core.service.dimensional_svc import DimensionalService, DimIntervaloTemporalService, TipoGranularidade

from .service.jira_svc import JiraService

logger = logging.getLogger(__name__)


def jira_healthcheck():
    """
    Function executed by cron to perform a healthcheck on the Jira API.
    This function is called by django-crontab according to the schedule configured
    in settings.py. It logs the result and can be expanded to send alerts in case of failure.
    """
    start_time = datetime.now()
    logger.info(f"[CRON] Starting Jira API healthcheck at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    success, message = JiraService.healthcheck()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    if success:
        logger.info(f"[CRON] Jira API healthcheck completed successfully in {duration:.2f}s: {message}")
    else:
        logger.error(f"[CRON] Jira API healthcheck failed after {duration:.2f}s: {message}")
    return success


def jira_sync_issues_all_projects():
    """
    Function executed by cron to sync issues for all projects at 3 AM.
    Fetches all projects from the database and calls JiraService.sync_all for each project.
    """
    start_time = datetime.now()
    logger.info(f"[CRON] Starting Jira issues sync for all projects at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        projects = Project.objects.all()
        for project in projects:
            logger.info(f"[CRON] Syncing issues for project {project.key}")
            JiraService.sync_all(project_key=project.key)
        logger.info("[CRON] Jira issues sync for all projects completed successfully.")
        return True
    except Exception as e:
        logger.error(f"[CRON] Jira issues sync failed: {e}")
        return False


def jira_project():
    """
    Function executed by cron to perform a healthcheck on the Jira API.
    This function is called by django-crontab according to the schedule configured
    in settings.py. It logs the result and can be expanded to send alerts in case of failure.
    """
    start_time = datetime.now()
    logger.info(f"[CRON] Starting Jira API projects at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    success, message = JiraService.get_projects()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    if success:
        logger.info(f"[CRON] Jira API healthcheck completed successfully in {duration:.2f}s: {message}")
    else:
        logger.error(f"[CRON] Jira API healthcheck failed after {duration:.2f}s: {message}")

    return success


def dimensional_load_daily():
    """
    Função executada por cron para carregar dados dimensionais.
    Esta função é chamada pelo django-crontab de acordo com a programação configurada
    em settings.py. Ela registra o resultado e pode ser expandida para enviar alertas em caso de falha.
    """
    start_time = datetime.now()
    logger.info(f"[CRON] Iniciando carga dimensional em {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        intervalo_tempo = DimIntervaloTemporalService(TipoGranularidade.DIA)
        success = DimensionalService.generate_project_snapshot_data(intervalo_tempo)
        if not success:
            logger.error("[CRON] Carga dimensional falhou")
            return
        success = DimensionalService.generate_fact_issue(intervalo_tempo)
        if not success:
            logger.error("[CRON] Carga dimensional falhou")
            return
        success = DimensionalService.generate_fact_worklog(intervalo_tempo)
        logger.info("[CRON] Carga dimensional concluída com sucesso.")
    except Exception as e:
        logger.error(f"[CRON] Carga dimensional falhou: {e}")
        raise e
    return True


def jira_full_sync():
    start_time = datetime.now()
    logger.info(f"[CRON] Starting FULL JIRA SYNC at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        projects_synced = jira_project()

        if projects_synced:
            issues_synced = jira_sync_issues_all_projects()
        else:
            logger.error("[CRON] Aborting issues sync because project sync failed.")
            issues_synced = False

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        if projects_synced and issues_synced:
            logger.info(f"[CRON] FULL JIRA SYNC finished successfully in {duration:.2f}s")
            return True
        else:
            logger.error(f"[CRON] FULL JIRA SYNC failed after {duration:.2f}s")
            return False
        
    except Exception as e:
        logger.critical(f"[CRON] A critical error occured during full sync: {e}", exc_info=True)
        return False
