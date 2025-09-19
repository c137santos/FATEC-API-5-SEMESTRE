import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

class JiraService:
    """Serviço para interação com a API do Jira"""
    
    @staticmethod
    def healthcheck():
        """
        Realiza um healthcheck na API do Jira verificando o endpoint de projetos.
        
        Returns:
            tuple: (success, message) onde success é um booleano indicando se o healthcheck foi bem-sucedido
                   e message é uma string com detalhes adicionais.
        """
        email = settings.JIRA_API_EMAIL
        token = settings.JIRA_API_TOKEN
        base_url = settings.JIRA_API_URL
        
        url = f"{base_url}/rest/api/3/project"
        
        logger.info(f"Realizando healthcheck na API do Jira: {url}")
        
        try:
            response = requests.get(
                url, 
                auth=(email, token),
                headers={"Accept": "application/json"}
            )
            
            if response.status_code == 200:
                projects_count = len(response.json())
                logger.info(f"Jira API healthcheck bem-sucedido. {projects_count} projetos encontrados.")
                return True, f"OK - {projects_count} projetos encontrados"
            else:
                logger.error(f"Jira API healthcheck falhou com status {response.status_code}: {response.text}")
                return False, f"Falhou com status {response.status_code}"
                
        except Exception as e:
            logger.exception("Erro durante o healthcheck da API do Jira")
            return False, str(e)