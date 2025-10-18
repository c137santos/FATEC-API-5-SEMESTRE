import logging
from datetime import date

from dateutil.relativedelta import relativedelta
from django.db.models import F, Sum

from ..models import Issue, Project, StatusType, TimeLog

logger = logging.getLogger(__name__)


def save_projects(projects_data):
    """
    Save or update a list of projects in the database.

    Args:
        projects_data (list[dict]): List of project dictionaries with Jira data.
    """
    for proj in projects_data:
        Project.objects.update_or_create(
            jira_id=proj["jira_id"],
            defaults={
                "key": proj.get("key"),
                "name": proj.get("name"),
                "description": proj.get("description", ""),
                "start_date_project": proj.get("start_date_project"),
                "end_date_project": proj.get("end_date_project"),
                "uuid": proj.get("uuid"),
                "jira_id": proj.get("jira_id"),
                "projectTypeKey": proj.get("projectTypeKey"),
            },
        )


def calc_start_date(issue_breakdown_months: int) -> date:
    today = date.today()
    return today.replace(day=1) - relativedelta(months=issue_breakdown_months - 1)


def build_issues_per_month(issues_qs, start_date: date, months: int):
    issues_per_month = []
    statuses = list(StatusType.objects.all())

    for i in range(months):
        month_date = start_date + relativedelta(months=i)
        month_label = month_date.isoformat()
        month_issues = issues_qs.filter(created_at__year=month_date.year, created_at__month=month_date.month)

        status_counts = {}
        for status in statuses:
            count = month_issues.filter(status__name=status.name).count()
            status_counts[status.name] = count

        issues_per_month.append(
            {
                "date": month_label,
                **status_counts,
            }
        )
    return issues_per_month


def serialize_project(project, project_issues):
    total_seconds = TimeLog.objects.filter(id_issue__in=project_issues).aggregate(total=Sum("seconds"))["total"] or 0

    total_hours = total_seconds / 3600 if total_seconds else 0

    total_issues = project_issues.count()

    dev_hours = (
        TimeLog.objects.filter(id_issue__in=project_issues)
        .values("id_user_id", "id_user__username")
        .annotate(hours=Sum(F("seconds") * 1.0) / 3600)
    )
    dev_hours_list = [
        {
            "dev_id": d["id_user_id"],
            "name": d["id_user__username"],
            "hours": round(d["hours"], 2) if d["hours"] is not None else 0,
        }
        for d in dev_hours
    ]
    return {
        "project_id": project.id,
        "name": project.name,
        "total_hours": round(total_hours, 2),
        "total_issues": total_issues,
        "dev_hours": dev_hours_list,
    }


def get_project_developers(project_id):
    from django.contrib.auth import get_user_model

    User = get_user_model()

    dev_time_data = (
        Issue.objects.filter(project__id=project_id, id_user__isnull=False)
        .values("id_user")
        .annotate(total_seconds=Sum(F("time_estimate_seconds")))
    )

    if not dev_time_data:
        return []

    developers = []

    for data in dev_time_data:
        user_id = data["id_user"]
        total_seconds = data["total_seconds"] or 0

        hours_worked = round(total_seconds / 3600) if total_seconds else 0

        developer_info = _get_developer_info(User, user_id, hours_worked)

        if developer_info:
            developers.append(developer_info)

    developers.sort(key=lambda dev: dev["horasTrabalhadas"], reverse=True)

    return developers


def _get_developer_info(User, user_id, hours_worked):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.warning(f"User ID {user_id} not found when building developer list")
        return None

    nome = user.get_full_name().strip() if user.get_full_name() else user.username

    valor_hora = _get_user_valor_hora(user)

    return {
        "id": user_id,
        "nome": nome,
        "horasTrabalhadas": hours_worked,
        "valorHora": valor_hora,
    }


def _get_user_valor_hora(user):
    if not hasattr(user, "valor_hora"):
        return None

    try:
        raw_value = user.valor_hora
        return float(raw_value) if raw_value is not None else None
    except (ValueError, TypeError) as e:
        logger.warning(f"Could not convert valor_hora for user {user.id}: {e}")
        return None


def list_projects_general(issue_breakdown_months: int):
    logger.info("Service list projects")
    start_date = calc_start_date(issue_breakdown_months)
    issues_qs = Issue.objects.filter(created_at__date__gte=start_date)

    issues_per_month = build_issues_per_month(issues_qs, start_date, issue_breakdown_months)

    projects = Project.objects.filter(issue__in=issues_qs).distinct().order_by("-start_date_project")

    projects_list = []
    for project in projects:
        project_issues = issues_qs.filter(project=project)
        projects_list.append(serialize_project(project, project_issues))

    return {"issues_per_month": issues_per_month, "projects": projects_list}
