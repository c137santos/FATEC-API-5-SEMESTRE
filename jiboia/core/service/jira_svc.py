import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

class JiraService:
    """Service for Jira API integration"""
    
    @staticmethod
    def healthcheck():
        """
        Performs a healthcheck on the Jira API by checking the projects endpoint.
        
        Returns:
            tuple: (success, message) where success is a boolean indicating if the healthcheck was successful
                   and message is a string with additional details.
        """
        email = settings.JIRA_API_EMAIL
        token = settings.JIRA_API_TOKEN
        base_url = settings.JIRA_API_URL
        
        url = f"{base_url}/rest/api/3/project"
        
        logger.info(f"Performing Jira API healthcheck: {url}")
        
        try:
            response = requests.get(
                url, 
                auth=(email, token),
                headers={"Accept": "application/json"}
            )
            
            if response.status_code == 200:
                projects_count = len(response.json())
                logger.info(f"Jira API healthcheck successful. {projects_count} projects found.")
                return True, f"OK - {projects_count} projects found"
            else:
                logger.error(f"Jira API healthcheck failed with status {response.status_code}: {response.text}")
                return False, f"Failed with status {response.status_code}"
                
        except Exception as e:
            logger.exception("Error during Jira API healthcheck")
            return False, str(e)