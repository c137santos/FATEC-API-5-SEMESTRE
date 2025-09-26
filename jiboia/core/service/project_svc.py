import logging
from datetime import date
from collections import Counter

from dateutil.relativedelta import relativedelta
from django.db.models import Sum

from ..models import Issue, Project, StatusLog, TimeLog

logger = logging.getLogger(__name__)

def group_issues_per_month(issues, start_date, end_date):
    results = []
    current = start_date

    while current <= end_date:
        month_issues = issues.filter(
            created_at__year=current.year,
            created_at__month=current.month,
        )

        counter = Counter({
            "pending": 0,
            "on_going": 0,
            "mr": 0,
            "concluded": 0,
        })

        for issue in month_issues:
            last_log = (
                issue.statuslog_set.order_by("-created_at")
                .select_related("new_status")
                .first()
            )
            if last_log and last_log.new_status:
                status_name = last_log.new_status.name.lower()
                if status_name in counter:
                    counter[status_name] += 1

        results.append({
            "date": current.strftime("%m/%Y"),
            "pending": counter["pending"],
            "on_going": counter["on_going"],
            "mr": counter["mr"],
            "concluded": counter["concluded"],
        })

        current += relativedelta(months=1)

    return results


def list_projects_general(issue_breakdown_months: int):
    logger.info("Service list projects")
    today = date.today()
    start_date = today.replace(day=1) - relativedelta(months=issue_breakdown_months - 1)
    
    issues = Issue.objects.filter(created_at__date__gte=start_date)

    issues_per_month = []
    for i in range(issue_breakdown_months):
        month_date = start_date + relativedelta(months=i)
        month_label = month_date.strftime("%m/%Y")

        month_issues = issues.filter(
            created_at__year=month_date.year,
            created_at__month=month_date.month
        )

        pending = StatusLog.objects.filter(
            id_issue__in=month_issues, new_status__name="pending"
        ).count()
        on_going = StatusLog.objects.filter(
            id_issue__in=month_issues, new_status__name="on_going"
        ).count()
        mr = StatusLog.objects.filter(
            id_issue__in=month_issues, new_status__name="mr"
        ).count()
        concluded = StatusLog.objects.filter(
            id_issue__in=month_issues, new_status__name="concluded"
        ).count()

        issues_per_month.append({
            "date": month_label,
            "pending": pending,
            "on_going": on_going,
            "mr": mr,
            "concluded": concluded
        })

    projects = Project.objects.filter(
        start_date_project__gte=start_date
    ).order_by("-start_date_project")

    projects_list = []
    for project in projects:
        project_issues = issues.filter(project=project)

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

        projects_list.append({
            "project_id": project.id,
            "name": project.name,
            "total_hours": total_hours,
            "total_issues": total_issues,
            "dev_hours": dev_hours_list,
        })

    return {
        "issues_per_month": issues_per_month,
        "projects": projects_list,
    }