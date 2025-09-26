import logging
from typing import Tuple, TypeVar

from django.conf import settings

from .strategy import JiraStrategy
from .strategy.healthcheck import ProjectsHealthCheckStrategy
from .strategy.issue_types import SyncIssueTypesStrategy
from .strategy.issues import SyncIssuesStrategy
from .strategy.status_types import SyncStatusTypesStrategy

logger = logging.getLogger(__name__)
T = TypeVar('T')


class JiraService:

    @classmethod
    def sync_all(cls, project_key: str = None) -> dict:
        """
        Synchronizes all Jira data by calling all implemented strategies.
        If project_key is provided, synchronizes issues for that project as well.
        Returns a dictionary with the result of each sync.
        """
        email, token, base_url = cls._get_credentials()
        results = {}
        results['issue_types'] = SyncIssueTypesStrategy(email, token, base_url).execute()
        results['status_types'] = SyncStatusTypesStrategy(email, token, base_url).execute()
        if project_key:
            results['issues'] = SyncIssuesStrategy(email, token, base_url).execute(project_key)
        return results
    
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
    def execute_strategy(cls, strategy: JiraStrategy[T]) -> T:
        """
        Execute a custom Jira API strategy.
        
        This method allows for executing any strategy that conforms to the JiraStrategy interface.
        
        Args:
            strategy: A strategy instance that conforms to the JiraStrategy interface
            
        Returns:
            T: The result of the strategy execution
        """
        return strategy.execute()