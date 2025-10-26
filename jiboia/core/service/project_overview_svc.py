import logging
from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone

from jiboia.core.service import issues_type_svc
from jiboia.core.service.dimensional_svc import DimIntervaloTemporalService, TipoGranularidade

from ..models import DimIntervaloTemporal, FactIssue, Issue, IssueType, Project, StatusType, TimeLog

logger = logging.getLogger(__name__)

FORMAT_DATE_MONTH = "%m/%Y"
FORMAT_DATE_COMPLETE = "%d/%m/%Y"


def _get_issues_per_month(project, issues_breakdown_months):
    """Helper function to get issues per month breakdown, with dynamic status fields."""
    issues_per_month = []
    interval_dict = DimIntervaloTemporalService.create_interval_retro(TipoGranularidade.MES, issues_breakdown_months)

    all_status_types = issues_type_svc.list_type_issues()
    status_keys = [status["name"].lower().replace(" ", "_").replace("-", "_") for status in all_status_types]
    status_dict_inited = {key: 0 for key in status_keys}

    for key, interval in interval_dict.items():
        start_date = interval["start_date"]
        dim_interval = DimIntervaloTemporal.objects.filter(
            granularity_type=TipoGranularidade.MES, start_date=start_date
        ).first()
        status_dict = status_dict_inited.copy()
        month_data = {"date": start_date.strftime(FORMAT_DATE_MONTH), **status_dict}

        if dim_interval:
            fatos = FactIssue.objects.filter(worklog_interval=dim_interval, project=project).select_related("status")

            for fato in fatos:
                status_key = fato.status.key.lower().replace(" ", "_").replace("-", "_")
                month_data[status_key] = month_data.get(status_key, 0) + (fato.total_issue or 0)
        issues_per_month.append(month_data)

    return issues_per_month


def _get_issues_today(project, all_status_types):
    """Helper function to get current issues breakdown"""
    today = timezone.now()
    issues_today = {"date": today.strftime(FORMAT_DATE_MONTH)}

    # Count current issues for each status type
    for status in all_status_types:
        count = Issue.objects.filter(project=project, status=status).count()

        status_key = status.key.lower().replace(" ", "_").replace("-", "_")
        issues_today[status_key] = count

    # Add count for issues with no status
    no_status_count = Issue.objects.filter(project=project, status__isnull=True).count()
    if no_status_count > 0:
        issues_today["no_status"] = no_status_count

    return issues_today


def _get_burndown_data(project, burndown_days):
    """Helper function to get burndown chart data"""
    today = timezone.now()
    burndown = {
        "end_date": (today + timedelta(days=burndown_days)).strftime(FORMAT_DATE_COMPLETE),
        "pending_per_day": [],
    }

    # Get pending status (assuming 'new', 'open', 'pending' keys)
    pending_statuses = StatusType.objects.filter(key__in=["new", "open", "pending", "todo", "backlog"])

    # Get total pending issues count
    total_pending = Issue.objects.filter(project=project, status__in=pending_statuses).count()

    if total_pending == 0:
        # If no pending issues, create empty burndown
        for i in range(burndown_days):
            date = today + timedelta(days=i)
            burndown["pending_per_day"].append({"date": date.strftime(FORMAT_DATE_COMPLETE), "pending": 0})
    else:
        # Calculate ideal burndown
        for i in range(burndown_days):
            date = today + timedelta(days=i)
            # Linear decrease: start with total_pending, end with 0
            expected_pending = max(0, total_pending - (total_pending * i // burndown_days))

            burndown["pending_per_day"].append(
                {"date": date.strftime(FORMAT_DATE_COMPLETE), "pending": expected_pending}
            )

    return burndown


def _get_total_worked_hours(project):
    """Helper function to calculate total worked hours for a project"""
    total_seconds = TimeLog.objects.filter(id_issue__project=project).aggregate(total=Sum("seconds"))["total"] or 0

    return round(total_seconds / 3600)


def _get_issues_by_type(project):
    """Helper function to get issues by type for a project"""
    issues_by_type = {}
    issue_types = IssueType.objects.all()

    for issue_type in issue_types:
        count = Issue.objects.filter(project=project, type_issue=issue_type).count()
        if count > 0:
            issues_by_type[issue_type.name.lower()] = count

    return issues_by_type


def _get_dev_hours(project):
    """Helper function to get developer hours for a project"""
    dev_hours = []

    # Get time logs grouped by user
    time_logs_by_user = (
        TimeLog.objects.filter(id_issue__project=project, id_user__isnull=False)
        .values("id_user", "id_user__username", "id_user__first_name", "id_user__last_name")
        .annotate(total_seconds=Sum("seconds"))
        .order_by("-total_seconds")
    )

    for entry in time_logs_by_user:
        if entry["total_seconds"]:
            # Try to build a proper name
            first_name = entry["id_user__first_name"] or ""
            last_name = entry["id_user__last_name"] or ""
            full_name = f"{first_name} {last_name}".strip()

            # Fallback to username if no first/last name
            display_name = full_name if full_name else (entry["id_user__username"] or f"User {entry['id_user']}")

            dev_hours.append(
                {"dev_id": entry["id_user"], "name": display_name, "hours": round(entry["total_seconds"] / 3600)}
            )

    return dev_hours


def get_project_overview(project_id, issues_breakdown_months=6, burndown_days=5):
    """
    Get detailed overview of a specific project

    Args:
        project_id (int): The ID of the project
        issues_breakdown_months (int): Number of months to include in issues breakdown
        burndown_days (int): Number of days to include in burndown chart

    Returns:
        dict: Project overview data or None if project not found
    """
    logger.info(f"Getting overview for project {project_id}")

    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        logger.error(f"Project with ID {project_id} not found")
        return None

    # Get all status types from the database
    all_status_types = StatusType.objects.all()

    # Build overview data
    overview = {
        "project_id": project.id,
        "name": project.name,
        "issues_per_month": _get_issues_per_month(project, issues_breakdown_months),
        "issues_today": _get_issues_today(project, all_status_types),
        "burndown": _get_burndown_data(project, burndown_days),
        "total_worked_hours": _get_total_worked_hours(project),
        "issues_status": _get_issues_by_type(project),
        "dev_hours": _get_dev_hours(project),
    }

    logger.info(f"Successfully generated overview for project {project_id}")
    return overview
