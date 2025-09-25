import logging
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from ..models import Project, Issue

logger = logging.getLogger(__name__)

def list_projects_general(issue_breakdown_months: int):
    logger.info("Service list projects")
    today = date.today()
    start_date = today.replace(day=1) - relativedelta(months=issue_breakdown_months - 1)
    
    projects_general = Project.objects.filter(
        start_date_project__gte=start_date
    ).order_by('-start_date_project')

    return [item.to_dict_json() for item in projects_general]

def list_projects_especific(project_id: int, issue_breakdown_months: int, burndown_days: int):
    today = date.today()

    start_date_monthly = today.replace(day=1) - relativedelta(months=issue_breakdown_months - 1)    
    
    start_date_burndown = today - timedelta(days=burndown_days)

    all_project_issues = Issue.objects.filter(project_id=project_id)
    
    issues_per_month = all_project_issues.filter(created_at__gte=start_date_monthly)

    issues_burndown = all_project_issues.filter(created_at__gte=start_date_burndown)

    return {
        "project_id": project_id,
        "issues_per_month": [i.to_dict_json() for i in issues_per_month],
        "issues_burndown": [i.to_dict_json() for i in issues_burndown],
    }