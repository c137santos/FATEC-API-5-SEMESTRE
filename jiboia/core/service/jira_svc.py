import logging
from typing import Tuple, TypeVar

from django.conf import settings

from jiboia.core.service.strategy.projects import ProjectsApiStrategy

from .strategy.healthcheck import ProjectsHealthCheckStrategy

logger = logging.getLogger(__name__)
T = TypeVar('T')


class JiraService:
    """Service for Jira API integration"""
    
    @classmethod
    def _get_credentials(cls) -> Tuple[str, str, str]:
        """Get Jira API credentials from settings"""
        return (
            settings.JIRA_API_EMAIL,
            settings.JIRA_API_TOKEN,
            settings.JIRA_API_URL
        )
    
    @classmethod
    def healthcheck(cls) -> Tuple[bool, str]:
        """
        Performs a healthcheck on the Jira API.
        
        Returns:
            tuple: (success, message) where success is a boolean indicating if the healthcheck was successful
                   and message is a string with additional details.
        """
        email, token, base_url = cls._get_credentials()
        strategy = ProjectsHealthCheckStrategy(email, token, base_url)
        return strategy.execute()
    
    
    @classmethod
    def get_projects(cls) -> T:
        """
        Fetch all projects from Jira.
        
        Returns:
            T: The list of projects retrieved from Jira
        """
        
        email, token, base_url = cls._get_credentials()
        strategy = ProjectsApiStrategy(email, token, base_url)
        projects_raw = strategy.execute()
        projects_dict = strategy.process(projects_raw)
        return strategy.save_projects(projects_dict)