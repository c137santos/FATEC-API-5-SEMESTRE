import logging
import requests
from .base import JiraStrategy
from jiboia.core.models import Project

logger = logging.getLogger(__name__)

class SyncProjectsStrategy(JiraStrategy[int]):
    """
    Sincroniza todos os projetos do Jira com o banco de dados local.
    Retorna a contagem total de projetos sincronizados.
    """
    _ENDPOINT = "/rest/api/3/project/search"
    _MAX_RESULTS = 50

    def execute(self) -> int:
        """
        Executa o processo de sincronização de projetos, lidando com paginação.
        """
        logger.info("Iniciando a sincronização de projetos do Jira...")
        synced_count = 0
        start_at = 0

        while True:
            params = {"startAt": start_at, "maxResults": self._MAX_RESULTS}
            response = self._make_request("get", self._ENDPOINT, params=params)
            response.raise_for_status()
            
            data = response.json()
            projects_data = data.get("values", [])

            if not projects_data:
                break

            for project_data in projects_data:
                try:
                    obj, created = Project.objects.update_or_create(
                        jira_id=project_data["id"],
                        defaults={
                            "key": project_data["key"],
                            "name": project_data["name"],
                            "description": project_data.get("description", ""),
                        },
                    )
                    log_action = "CRIADO" if created else "ATUALIZADO"
                    logger.info(f"Projeto '{obj.name}' {log_action}.")
                    synced_count += 1
                except Exception as e:
                    logger.error(f"Falha ao sincronizar projeto com jira_id {project_data.get('id')}: {e}")

            if data.get("isLast", True):
                break
            
            start_at += len(projects_data)

        logger.info(f"Sincronização de projetos concluída. Total: {synced_count}.")
        return synced_count