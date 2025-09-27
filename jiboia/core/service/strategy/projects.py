"""Health check strategies for Jira API."""

import abc
import logging
from typing import Tuple

from jiboia.core.service import projects_svc

from .base import JiraStrategy

logger = logging.getLogger(__name__)


class ProjectsStrategy(JiraStrategy[Tuple[bool, str]], abc.ABC):
    """Base class for health check strategies."""
    
    @abc.abstractmethod
    def execute(self) -> str:
        """
        Execute health check strategy.
        
        Returns:
            tuple: (success, message) - success state and descriptive message
        """
        pass

    @abc.abstractmethod
    def process(self, data) -> list[dict]:
        """
        Process raw data from Jira API into a list of project dictionaries.
        
        Args:
            data: Raw data from Jira API.       
        Returns:
            list[dict]: Processed list of project dictionaries.
        """
        pass

    @abc.abstractmethod
    def save_projects(self, projects_dict: list[dict]) -> Tuple[bool, str]:
        """
        Save or update projects in the database.    
        Args:
            projects_dict (list[dict]): List of project dictionaries with Jira data.
        Returns:
            tuple: (success, message) - success state and descriptive message
        """
        pass


class ProjectsApiStrategy(ProjectsStrategy):
    """Strategy that get the projects in endpoint"""
    
    def execute(self) -> str:
        endpoint = "/rest/api/3/project"
        logger.info(f"Performing Jira API on projects endpoint: {endpoint}")
        
        try:
            response = self._make_request('get', endpoint)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Jira API healthcheck failed with status {response.status_code}: {response.text}")
                return f"Failed with status {response.status_code}"
                
        except Exception as e:
            logger.exception("Error during Jira API projects endpoint")
            return str(e)
        
    def process(self, data) -> list[dict]:
        projects = []
        for proj in data:
            projects.append({
                "jira_id": proj["id"],
                "uuid": proj.get("uuid"),
                "key": proj.get("key"),
                "name": proj.get("name"),
                "projectTypeKey": proj.get("projectTypeKey"),
                "simplified": proj.get("simplified"),
                "start_date_project": proj.get("start_date_project"),
                "end_date_project": proj.get("end_date_project"),
            })
        return projects
        
    def save_projects(self, projects_dict: list[dict]) -> Tuple[bool, str]:
        
        try:
            projects_svc.save_projects(projects_dict)
            return True, f"Successfully saved {len(projects_dict)} projects."
        except Exception as e:
            logger.exception("Error saving projects to the database")
            return False, str(e)
    
        
        
        