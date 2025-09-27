import logging
import datetime
from calendar import monthrange
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from ..models import Project, Issue, IssueType, TimeLog, StatusType

logger = logging.getLogger(__name__)

def get_project_overview(project_id, issues_breakdown_months=6, burndown_days=5):
    """
    Get detailed overview of a specific project
    
    Args:
        project_id (int): The ID of the project
        issues_breakdown_months (int): Number of months to include in issues breakdown
        burndown_days (int): Number of days to include in burndown chart
        
    Returns:
        dict: Project overview data
    """
    logger.info(f"SERVICE getting overview for project {project_id}")
    
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        logger.error(f"Project with ID {project_id} not found")
        return None
    
    today = timezone.now()
    
    # Get all status types from the database
    all_status_types = StatusType.objects.all()
    
    issues_per_month = []
    for i in range(issues_breakdown_months - 1, -1, -1):
        date_month = today - timedelta(days=30 * i)
        month_start = date_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end_day = monthrange(date_month.year, date_month.month)[1]
        month_end = date_month.replace(day=month_end_day, hour=23, minute=59, second=59, microsecond=999999)
        
        # Dictionary to hold counts for each status
        month_data = {"date": date_month.strftime("%m/%Y")}
        
        # Count issues for each status type
        for status in all_status_types:
            count = Issue.objects.filter(
                project=project,
                created_at__lte=month_end,
                status=status
            ).count()
            
            status_key = status.key.lower().replace(' ', '_').replace('-', '_')
            month_data[status_key] = count
        
        no_status_count = Issue.objects.filter(
            project=project,
            created_at__lte=month_end,
            status__isnull=True
        ).count()
        if no_status_count > 0:
            month_data["no_status"] = no_status_count
        
        issues_per_month.append(month_data)
    # Today's issues breakdown using actual status values
    issues_today = {"date": today.strftime("%m/%Y")}
    
    # Count issues for each status type
    for status in all_status_types:
        count = Issue.objects.filter(
            project=project,
            status=status
        ).count()
        
        status_key = status.key.lower().replace(' ', '_').replace('-', '_')
        issues_today[status_key] = count
    
    # Add count for issues with no status as "no_status" 
    no_status_count = Issue.objects.filter(
        project=project,
        status__isnull=True
    ).count()
    if no_status_count > 0:
        issues_today["no_status"] = no_status_count
    
    # Burndown chart data
    burndown = {
        "end_date": (today + timedelta(days=burndown_days)).strftime("%d/%m/%Y"),
        "pending_per_day": []
    }
    
    pending_issues = Issue.objects.filter(project=project).count()
    
    for i in range(burndown_days):
        date = today + timedelta(days=i)
        expected_pending = max(0, pending_issues - (pending_issues // burndown_days) * i)
        
        burndown["pending_per_day"].append({
            "date": date.strftime("%d/%m/%Y"),
            "pending": expected_pending
        })
    
    total_worked_hours = TimeLog.objects.filter(
        id_issue__project=project
    ).aggregate(total=Sum('seconds'))['total'] or 0
    
    total_worked_hours = round(total_worked_hours / 3600)
    
    issues_by_type = {}
    issue_types = IssueType.objects.all()
    for issue_type in issue_types:
        count = Issue.objects.filter(project=project, type_issue=issue_type).count()
        if count > 0:
            issues_by_type[issue_type.name.lower()] = count
    
    dev_hours = []
    time_logs_by_user = TimeLog.objects.filter(
        id_issue__project=project
    ).values('id_user', 'id_user__username').annotate(
        total_seconds=Sum('seconds')
    )
    
    for entry in time_logs_by_user:
        if entry['id_user'] and entry['total_seconds']:
            dev_hours.append({
                "dev_id": entry['id_user'],
                "name": entry['id_user__username'],
                "hours": round(entry['total_seconds'] / 3600)
            })
    
    overview = {
        "project_id": project.id,
        "name": project.name,
        "issues_per_month": issues_per_month,
        "issues_today": issues_today,
        "burndown": burndown,
        "total_worked_hours": total_worked_hours,
        "issues_status": issues_by_type,
        "dev_hours": dev_hours
    }
    
    return overview