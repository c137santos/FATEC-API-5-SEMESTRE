import logging
from datetime import date

from dateutil.relativedelta import relativedelta
from django.db.models import Sum

from ..models import Issue, Project, StatusLog, StatusType, TimeLog

logger = logging.getLogger(__name__)

def calc_start_date(issue_breakdown_months: int) -> date:
    today = date.today()
    return today.replace(day=1) - relativedelta(months=issue_breakdown_months - 1)

def build_issues_per_month(issues_qs, start_date: date, months: int):
    issues_per_month = []
    statuses = list(StatusType.objects.all())
    
    for i in range(months):
        month_date = start_date + relativedelta(months=i)
        month_label = month_date.isoformat()
        month_issues = issues_qs.filter(
            created_at__year=month_date.year,
            created_at__month=month_date.month
        )

        status_counts = {
            status.name: StatusLog.objects.filter(
                id_issue__in=month_issues, new_status__name=status.name
            ).count()

            for status in statuses
        }

        issues_per_month.append({
            "date": month_label,
            **status_counts,
        })
    return issues_per_month

def serialize_project(project, project_issues):
    total_hours = TimeLog.objects.filter(
        id_issue__in=project_issues
    ).aggregate(total=Sum("seconds"))["total"] or 0
    
    total_issues = project_issues.count()
    
    dev_hours = (
        TimeLog.objects.filter(id_issue__in=project_issues)
        .values("id_user_id", "id_user__username")
        .annotate(hours=Sum("seconds"))
    )
    dev_hours_list = [
        {
            "dev_id": d["id_user_id"],
            "name": d["id_user__username"],
            "hours": d["hours"] or 0,
        }
        for d in dev_hours
    ]
    return {
        "project_id": project.id,
        "name": project.name,
        "total_hours": total_hours,
        "total_issues": total_issues,
        "dev_hours": dev_hours_list,
    }

def list_projects_general(issue_breakdown_months: int):
    logger.info("Service list projects")
    start_date = calc_start_date(issue_breakdown_months)
    issues_qs = Issue.objects.filter(created_at__date__gte=start_date)

    issues_per_month = build_issues_per_month(issues_qs, start_date, issue_breakdown_months)

    projects = Project.objects.filter(
        start_date_project__gte=start_date
    ).order_by("-start_date_project")
    
    projects_list = []
    for project in projects:
        project_issues = issues_qs.filter(project=project)
        projects_list.append(serialize_project(project, project_issues))

    return {"issues_per_month": issues_per_month, "projects": projects_list}