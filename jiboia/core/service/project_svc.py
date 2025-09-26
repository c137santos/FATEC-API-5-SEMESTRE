import logging
from collections import Counter
from datetime import date

from dateutil.relativedelta import relativedelta

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


def calc_start_date(issue_breakdown_months: int) -> date:
    today = date.today()
    return today.replace(day=1) - relativedelta(months=issue_breakdown_months - 1)


def build_issues_per_month(issues_qs, start_date: date, months: int):
    issues_per_month = []
    for i in range(months):
        month_date = start_date + relativedelta(months=i)
        month_label = month_date.strftime("%m/%Y")
        month_issues = Issue.for_month(issues_qs, month_date)

        pending = StatusLog.count_by_status_for_issues(month_issues, "pending")
        on_going = StatusLog.count_by_status_for_issues(month_issues, "on_going")
        mr = StatusLog.count_by_status_for_issues(month_issues, "mr")
        concluded = StatusLog.count_by_status_for_issues(month_issues, "concluded")

        issues_per_month.append({
            "date": month_label,
            "pending": pending,
            "on_going": on_going,
            "mr": mr,
            "concluded": concluded,
        })
    return issues_per_month


def serialize_project(project, project_issues):
    total_hours = TimeLog.total_seconds_for_issues(project_issues)
    total_issues = project_issues.count()
    dev_hours = TimeLog.dev_hours_for_issues(project_issues)
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
    issues_qs = Issue.created_since_month_start_back(start_date)

    issues_per_month = build_issues_per_month(issues_qs, start_date, issue_breakdown_months)

    projects = Project.starting_since(start_date)
    projects_list = []
    for project in projects:
        project_issues = Issue.for_project(issues_qs, project)
        projects_list.append(serialize_project(project, project_issues))

    return {"issues_per_month": issues_per_month, "projects": projects_list}