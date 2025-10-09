import logging

from jiboia.core.models import IssueType

from .base import JiraStrategy

logger = logging.getLogger(__name__)


class SyncIssueTypesStrategy(JiraStrategy[int]):
    """
    Synchronizes all Jira Issue Types with the local database.
    """

    _ENDPOINT = "/rest/api/3/issuetype"

    def execute(self) -> int:
        """
        Executes the synchronization process for issue types.
        """
        logger.info("Starting synchronization of Issue Types...")
        synced_count = 0
        response = self._make_request("get", self._ENDPOINT)
        response.raise_for_status()
        for type_data in response.json():
            try:
                obj, created = IssueType.objects.update_or_create(
                    jira_id=type_data["id"],
                    defaults={
                        "name": type_data["name"],
                        "description": type_data.get("description", ""),
                        "subtask": type_data.get("subtask", False),
                    },
                )
                log_action = "CREATED" if created else "UPDATED"
                logger.info(f"Issue Type '{obj.name}' {log_action}.")
                synced_count += 1
            except Exception as e:
                logger.error(f"Failed to sync issue type with jira_id {type_data.get('id')}: {e}")
        logger.info(f"Issue Types synchronization finished. Total: {synced_count}.")
        return synced_count
