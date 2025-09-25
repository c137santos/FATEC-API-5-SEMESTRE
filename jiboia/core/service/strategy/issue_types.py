import logging

from jiboia.core.models import IssueType

from .base import JiraStrategy

logger = logging.getLogger(__name__)

class SyncIssueTypesStrategy(JiraStrategy[int]):
    """
    Sincroniza todos os tipos de issue (Issue Types) do Jira.
    """
    _ENDPOINT = "/rest/api/3/issuetype"

    def execute(self) -> int:
        """
        Executa o processo de sincronização dos tipos de issue.
        """
        logger.info("Iniciando a sincronização de Tipos de Issue...")
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
                log_action = "CRIADO" if created else "ATUALIZADO"
                logger.info(f"Tipo de Issue '{obj.name}' {log_action}.")
                synced_count += 1
            except Exception as e:
                logger.error(f"Falha ao sincronizar tipo de issue com jira_id {type_data.get('id')}: {e}")

        logger.info(f"Sincronização de Tipos de Issue concluída. Total: {synced_count}.")
        return synced_count