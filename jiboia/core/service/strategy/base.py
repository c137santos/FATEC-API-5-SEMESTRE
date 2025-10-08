"""Base Jira strategy implementation."""

import abc
from typing import Generic, TypeVar

import requests

T = TypeVar('T')


class JiraStrategy(Generic[T], abc.ABC):
    """Abstract base class for Jira API interaction strategies"""
    
    def __init__(self, email: str, token: str, base_url: str):
        self.email = email
        self.token = token
        self.base_url = base_url
        self.auth = (email, token)
        self.headers = {"Accept": "application/json"}
    
    @abc.abstractmethod
    def execute(self, project_key: str) -> T:
        """
        Execute the API call strategy.
        
        Returns:
            T: The result of the strategy execution, type depends on the specific strategy
        """
        pass
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make a request to the Jira API.
        
        Args:
            method: HTTP method (get, post, put, delete)
            endpoint: API endpoint path (without base URL)
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            requests.Response: The response from the API
        """
        url = f"{self.base_url}{endpoint}"
        
        # Add auth and headers to kwargs if not explicitly provided
        if 'auth' not in kwargs:
            kwargs['auth'] = self.auth
        if 'headers' not in kwargs:
            kwargs['headers'] = self.headers
        
        return getattr(requests, method.lower())(url, **kwargs)