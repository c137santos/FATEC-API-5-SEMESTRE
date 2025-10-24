import logging
from datetime import datetime

from django.utils import timezone

from jiboia.core.models import DimIntervaloTemporal, Project
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


def dimensional_load(time_interval):
    """
    Função executada por cron para carregar dados dimensionais.
    Esta função é chamada pelo django-crontab de acordo com a programação configurada
    em settings.py. Ela registra o resultado e pode ser expandida para enviar alertas em caso de falha.
    """
    start_time = datetime.now()
    logger.info(f"[CRON] Iniciando carga dimensional em diário {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        success = DimensionalService.generate_project_snapshot_data(time_interval)
        if not success:
            logger.error("[CRON] Carga dimensional falhou")
            return
        success = DimensionalService.generate_fact_issue(time_interval)
        if not success:
            logger.error("[CRON] Carga dimensional falhou")
            return
        success = DimensionalService.generate_fact_worklog(time_interval)
        logger.info("[CRON] Carga dimensional concluída com sucesso.")
    except Exception as e:
        logger.error(f"[CRON] Carga dimensional falhou: {e}")
        raise e
    return True


def dimensional_load_daily():
    start_time = datetime.now()
    logger.info(f"[CRON] Iniciando carga dimensional em diário {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    intervalo_tempo = DimIntervaloTemporalService(TipoGranularidade.DIA)
    if prevent_redundant_cron(intervalo_tempo, TipoGranularidade.DIA.value):
        logger.error(
            (
                f"[CRON] Carga dimensional do tipo {TipoGranularidade.DIA.value} já existente "
                f"para o período {intervalo_tempo.start_date} a {intervalo_tempo.end_date}. "
                "Operação abortada."
            )
        )
        return False
    return dimensional_load(intervalo_tempo)


def load_dimensional_weekly():
    start_time = datetime.now()
    logger.info(f"[CRON] Iniciando carga dimensional em semanal {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    intervalo_tempo = DimIntervaloTemporalService(TipoGranularidade.SEMANA)
    if prevent_redundant_cron(intervalo_tempo, TipoGranularidade.SEMANA.value):
        logger.error(
            (
                f"[CRON] Carga dimensional do tipo {TipoGranularidade.SEMANA.value} já existente "
                f"para o período {intervalo_tempo.start_date} a {intervalo_tempo.end_date}. "
                "Operação abortada."
            )
        )
        return False
    return dimensional_load(intervalo_tempo)


def load_dimensional_monthly():
    start_time = datetime.now()
    logger.info(f"[CRON] Iniciando carga dimensional em mensal {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    intervalo_tempo = DimIntervaloTemporalService(TipoGranularidade.MES)
    if prevent_redundant_cron(intervalo_tempo, TipoGranularidade.MES.value):
        logger.error(
            (
                f"[CRON] Carga dimensional do tipo {TipoGranularidade.MES.value} já existente "
                f"para o período {intervalo_tempo.start_date} a {intervalo_tempo.end_date}. "
                "Operação abortada."
            )
        )
        return False
    return dimensional_load(intervalo_tempo)


def load_dimensional_quarterly():
    start_time = datetime.now()
    logger.info(f"[CRON] Iniciando carga dimensional em trimestre {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    intervalo_tempo = DimIntervaloTemporalService(TipoGranularidade.TRIMESTRE)
    if prevent_redundant_cron(intervalo_tempo, TipoGranularidade.TRIMESTRE.value):
        logger.error(
            (
                f"[CRON] Carga dimensional do tipo {TipoGranularidade.TRIMESTRE.value} já existente "
                f"para o período {intervalo_tempo.start_date} a {intervalo_tempo.end_date}. "
                "Operação abortada."
            )
        )
        return False
    return dimensional_load(intervalo_tempo)


def load_dimensional_semester():
    start_time = datetime.now()
    logger.info(f"[CRON] Iniciando carga dimensional em semestre {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    intervalo_tempo = DimIntervaloTemporalService(TipoGranularidade.SEMESTRE)
    if prevent_redundant_cron(intervalo_tempo, TipoGranularidade.SEMESTRE.value):
        logger.error(
            (
                f"[CRON] Carga dimensional do tipo {TipoGranularidade.SEMESTRE.value} já existente "
                f"para o período {intervalo_tempo.start_date} a {intervalo_tempo.end_date}. "
                "Operação abortada."
            )
        )
        return False
    return dimensional_load(intervalo_tempo)


def load_dimensional_yearly():
    start_time = datetime.now()
    logger.info(f"[CRON] Iniciando carga dimensional em anual {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    intervalo_tempo = DimIntervaloTemporalService(TipoGranularidade.ANO)
    if prevent_redundant_cron(intervalo_tempo, TipoGranularidade.ANO.value):
        logger.error(
            (
                f"[CRON] Carga dimensional do tipo {TipoGranularidade.ANO.value} já existente "
                f"para o período {intervalo_tempo.start_date} a {intervalo_tempo.end_date}. "
                "Operação abortada."
            )
        )
        return False
    return dimensional_load(intervalo_tempo)


def load_dimensional_all():
    start_time = datetime.now()
    logger.info(f"[CRON] Iniciando carga dimensional completa {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        i = 0
        for tipo in TipoGranularidade:
            print(i + 1, tipo.value)
            start_date, end_date = DimIntervaloTemporalService.create_interval(tipo)

            if timezone.is_naive(start_date):
                start_date = timezone.make_aware(start_date)
            if timezone.is_naive(end_date):
                end_date = timezone.make_aware(end_date)

            if prevent_redundant_cron(start_date, end_date, tipo.value):
                continue
            temporal_int = DimIntervaloTemporalService(tipo)
            dimensional_load(temporal_int)
        logger.info("[CRON] Carga dimensional completa concluída com sucesso.")
        return True
    except Exception as e:
        logger.error(f"[CRON] Carga dimensional completa falhou: {e}")
        return False


def prevent_redundant_cron(start_date, end_date, gran_type):
    exists = DimIntervaloTemporal.objects.filter(
        granularity_type=gran_type,
        start_date=start_date,
        end_date=end_date,
    ).exists()
    if exists:
        logger.error(f"[CRON] Já existe carga dimensional {gran_type} para {start_date}. Operação abortada.")
        return True
    return False
