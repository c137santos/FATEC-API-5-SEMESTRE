import logging

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


def list_issues():
    logger.info("SERVICE list issues")
    issues_list = Issue.objects.all()
    return [item.to_dict_json() for item in issues_list]
