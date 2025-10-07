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
    issues_list = Issue.objects.all().order_by('-id')
    paginator = Paginator(issues_list, 10)

    try:
        page = paginator.page(page_number)
        issues_data = [item.to_dict_json() for item in issues_list]
        return {
            'issues': issues_data,
            'current_page': page_number,
            'total_pages': paginator.num_pages,
            'has_next': page.has_next(),
            'has_previous': page.has_previous(),
            'total_items': paginator.count,
        }

    except Exception:
        return {
            'issues': [],
            'current_page': page_number,
            'total_pages': paginator.num_pages,
            'has_next': False,
            'has_previous': page_number > 1,
            'total_items': paginator.count,
        }