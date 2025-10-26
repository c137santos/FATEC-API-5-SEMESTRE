import logging

from django.core.paginator import Paginator

from jiboia.base.exceptions import BusinessError

from ..models import Issue

logger = logging.getLogger(__name__)


def add_issue(new_issue: str) -> dict:
    logger.info("SERVICE add new issue")
    if not isinstance(new_issue, str):
        raise BusinessError("Invalid description")

    if not new_issue or not new_issue.strip():
        raise BusinessError("Invalid description")

    issue = Issue(description=new_issue)
    issue.save()
    logger.info("SERVICE issue created.")
    return issue.to_dict_json()


def list_issues(project_id: int, page_number: int = 1, per_page: int = 10):
    logger.info(f"SERVICE list issues for project {project_id}")

    issues_list = Issue.objects.filter(project_id=project_id).select_related("id_user", "status", "project")

    issues_list = issues_list.defer("id_user__jira_id").order_by("-id")

    paginator = Paginator(issues_list, per_page)

    try:
        page = paginator.page(page_number)
        issues_data = []

        for item in page:
            issue_dict = item.to_dict_json()

            issue_dict.pop("start_date", None)
            issue_dict.pop("end_date", None)

            user_name = None
            user_id = None
            if item.id_user:
                user_name = item.id_user.get_full_name()
                user_id = item.id_user.id

            time_spend_hours = 0
            if item.time_estimate_seconds:
                time_spend_hours = item.time_estimate_seconds / 3600

            issue_dict.update(
                {
                    "jira_id": item.jira_id,
                    "user_related": {"id": user_id, "user_name": user_name} if item.id_user else None,
                    "time_spend_hours": time_spend_hours,
                }
            )
            issues_data.append(issue_dict)

        return {
            "issues": issues_data,
            "current_page": page_number,
            "total_pages": paginator.num_pages,
            "total_items": paginator.count,
        }

    except Exception as e:
        logger.error(f"SERVICE error listing issues for project {project_id}: {e}", exc_info=True)
        return {
            "issues": [],
            "current_page": page_number,
            "total_pages": paginator.num_pages,
            "total_items": paginator.count,
        }
