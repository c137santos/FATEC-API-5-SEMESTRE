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

    start_of_period_monthly = today.replace(day=1)
    start_date_monthly = start_of_period_monthly - relativedelta(months=issue_breakdown_months - 1)    
    
    start_date_burndown = today - timedelta(days=burndown_days)
    all_project_issues = Issue.objects.filter(project_id=project_id)

    issues_per_month_data = aggregate_by_month(all_project_issues, start_date_monthly)

    burndown_data = aggregate_burndown(all_project_issues, start_date_burndown)

    total_hours = calculate_total_hours(all_project_issues)
    status_counts = calculate_status_counts(all_project_issues)
    dev_hours = calculate_dev_hours(all_project_issues)

    return {
        "project_id": project_id,
        "issues_per_month": issues_per_month_data,
        "issues_today": {}, 
        "burndown": burndown_data,
        "total_worked_hours": total_hours,
        "issues_status": status_counts,
        "dev_hours": dev_hours
    }