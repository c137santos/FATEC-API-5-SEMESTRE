import logging
import requests
from .base import JiraStrategy
from jiboia.core.models import StatusType

logger = logging.getLogger(__name__)

class SyncStatusTypesStrategy(JiraStrategy[int]):
    """
    Sincroniza todos os status (Status Types) do Jira.
    """
    _ENDPOINT = "/rest/api/3/status"

    def execute(self) -> int:
        """
        Executa o processo de sincronização de status.
        """
        logger.info("Iniciando a sincronização de Status...")
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
                log_action = "CRIADO" if created else "ATUALIZADO"
                logger.info(f"Status '{obj.name}' {log_action}.")
                synced_count += 1
            except Exception as e:
                logger.error(f"Falha ao sincronizar status com jira_id {status_data.get('id')}: {e}")
        
        logger.info(f"Sincronização de Status concluída. Total: {synced_count}.")
        return synced_count