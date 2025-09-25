import logging
from datetime import datetime

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