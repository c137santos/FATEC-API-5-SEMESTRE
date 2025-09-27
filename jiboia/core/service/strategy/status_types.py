import logging

from jiboia.core.models import StatusType

from .base import JiraStrategy

logger = logging.getLogger(__name__)

class SyncStatusTypesStrategy(JiraStrategy[int]):
    """
    Synchronizes all Jira Status Types with the local database.
    """
    _ENDPOINT = "/rest/api/3/status"

    def execute(self) -> int:
        """
        Executes the synchronization process for status types.
        """
        logger.info("Starting synchronization of Status Types...")
        synced_count = 0
        response = self._make_request("get", self._ENDPOINT)
        response.raise_for_status()
        for status_data in response.json():
            try:
                category = status_data.get("statusCategory", {})
                obj, created = StatusType.objects.update_or_create(
                    jira_id=status_data["id"],
                    defaults={
                        "name": status_data["name"],
                        "key": category.get("key", "undefined"),
                    },
                )
                log_action = "CREATED" if created else "UPDATED"
                logger.info(f"Status '{obj.name}' {log_action}.")
                synced_count += 1
            except Exception as e:
                logger.error(f"Failed to sync status with jira_id {status_data.get('id')}: {e}")
        logger.info(f"Status Types synchronization finished. Total: {synced_count}.")
        return synced_count