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


def list_issues(page_number: int = 1):
    logger.info("SERVICE list issues")
    issues_list = Issue.objects.all().select_related('id_user', 'status').order_by('-id')
    paginator = Paginator(issues_list, 10)

    try:
        page = paginator.page(page_number)
        issues_data = []

        for item in page:
            issue_dict = item.to_dict_json()

            user_name = None
            if item.id_user:
                user_name = item.id_user.get_full_name()

            issue_dict.update({
                "jira_id": item.jira_id,
                "user_related": {
                    "id": item.id_user.id,
                    "user_name": user_name
                } if item.id_user else None,
                "time_spend_hours": item.time_estimate_seconds / 3600,
            })
            issues_data.append(issue_dict)

        return {
            'issues': issues_data,
            'current_page': page_number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
        }

    except Exception:
        return {
            'issues': [],
            'current_page': page_number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count
        }