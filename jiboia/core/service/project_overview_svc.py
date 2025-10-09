import logging
from calendar import monthrange
from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone

from ..models import Issue, IssueType, Project, StatusType, TimeLog

logger = logging.getLogger(__name__)

FORMAT_DATE_MONTH = "%m/%Y"
FORMAT_DATE_COMPLETE = "%d/%m/%Y"


def _get_issues_per_month(project, all_status_types, issues_breakdown_months):
    """Helper function to get issues per month breakdown"""
    issues_per_month = []
    today = timezone.now()

    for i in range(issues_breakdown_months - 1, -1, -1):
        date_month = today - timedelta(days=30 * i)
        month_start = date_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end_day = monthrange(date_month.year, date_month.month)[1]
        month_end = date_month.replace(day=month_end_day, hour=23, minute=59, second=59, microsecond=999999)

        # Dictionary to hold counts for each status
        month_data = {"date": date_month.strftime(FORMAT_DATE_MONTH)}

        # Count issues created in this month for each status type
        for status in all_status_types:
            count = Issue.objects.filter(
                project=project, created_at__gte=month_start, created_at__lte=month_end, status=status
            ).count()

            status_key = status.key.lower().replace(" ", "_").replace("-", "_")
            month_data[status_key] = count

        # Count issues created in this month with no status
        no_status_count = Issue.objects.filter(
            project=project, created_at__gte=month_start, created_at__lte=month_end, status__isnull=True
        ).count()
        if no_status_count > 0:
            month_data["no_status"] = no_status_count

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
        "issues_per_month": _get_issues_per_month(project, all_status_types, issues_breakdown_months),
        "issues_today": _get_issues_today(project, all_status_types),
        "burndown": _get_burndown_data(project, burndown_days),
        "total_worked_hours": _get_total_worked_hours(project),
        "issues_status": _get_issues_by_type(project),
        "dev_hours": _get_dev_hours(project),
    }

    logger.info(f"Successfully generated overview for project {project_id}")
    return overview
