"""Health check strategies for Jira API."""

import abc
import logging
from typing import Tuple

from .base import JiraStrategy

logger = logging.getLogger(__name__)


class HealthCheckStrategy(JiraStrategy[Tuple[bool, str]], abc.ABC):
    """Base class for health check strategies."""
    
    @abc.abstractmethod
    def execute(self) -> Tuple[bool, str]:
        """
        Execute health check strategy.
        
        Returns:
            tuple: (success, message) - success state and descriptive message
        """
        pass


class ProjectsHealthCheckStrategy(HealthCheckStrategy):
    """Strategy that checks health by verifying the projects endpoint"""
    
    def execute(self) -> Tuple[bool, str]:
        """
        Execute health check by querying the projects endpoint.
        
        Returns:
            tuple: (success, message) - success state and descriptive message
        """
        endpoint = "/rest/api/3/project"
        logger.info(f"Performing Jira API healthcheck on projects endpoint: {endpoint}")
        
        try:
            response = self._make_request('get', endpoint)
            
            if response.status_code == 200:
                projects_count = len(response.json())
                logger.info(f"Jira API healthcheck successful. {projects_count} projects found.")
                return True, f"OK - {projects_count} projects found"
            else:
                logger.error(f"Jira API healthcheck failed with status {response.status_code}: {response.text}")
                return False, f"Failed with status {response.status_code}"
                
        except Exception as e:
            logger.exception("Error during Jira API healthcheck on projects endpoint")
            return False, str(e)