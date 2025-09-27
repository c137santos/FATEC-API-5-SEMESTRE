"""Tests for ProjectsStrategy."""

from unittest.mock import patch

from jiboia.core.service.strategy.projects import ProjectsApiStrategy


@patch('jiboia.core.service.strategy.base.requests.get')
def test_projects_strategy_success(mock_get, mock_response, projects_data):
    """Test successful projects fetch."""
    mock_response.status_code = 200
    mock_response.json.return_value = projects_data
    mock_get.return_value = mock_response

    strategy = ProjectsApiStrategy('test@example.com', 'token123', 'https://jira.example.com')
    data = strategy.execute()

    assert data == projects_data
    mock_get.assert_called_once()


@patch('jiboia.core.service.strategy.base.requests.get')
def test_projects_strategy_empty_response(mock_get, mock_response):
    """Test projects fetch with empty response."""
    mock_response.status_code = 200
    mock_response.json.return_value = []
    mock_get.return_value = mock_response

    strategy = ProjectsApiStrategy('test@example.com', 'token123', 'https://jira.example.com')
    data = strategy.execute()

    assert data == []
    mock_get.assert_called_once()


@patch('jiboia.core.service.strategy.base.requests.get')
def test_projects_strategy_http_error(mock_get, mock_response):
    """Test projects fetch with HTTP error."""
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_get.return_value = mock_response

    strategy = ProjectsApiStrategy('test@example.com', 'token123', 'https://jira.example.com')
    data = strategy.execute()

    assert "Failed with status 404" in data
    mock_get.assert_called_once()


@patch('jiboia.core.service.strategy.base.requests.get')
def test_projects_strategy_exception(mock_get):
    """Test projects fetch with exception."""
    mock_get.side_effect = Exception("Connection error")

    strategy = ProjectsApiStrategy('test@example.com', 'token123', 'https://jira.example.com')
    data = strategy.execute()

    assert "Connection error" in data



def test_projects_strategy_process(projects_data):
    strategy = ProjectsApiStrategy('test@example.com', 'token123', 'https://jira.example.com')
    processed = strategy.process(projects_data)
    assert  processed == [{
      "jira_id":"10200",
      "uuid":"e915ce14-18fc-417a-92fb",
      "key":"SM2",
      "name":"SOS MNT 2025",
      "projectTypeKey":"software",
      "simplified":True,
      "start_date_project": None,
      "end_date_project": None
   },
   {
      "jira_id":"10202",
      "uuid":"950c63a2-e6bb-4e5d-8390",
      "key":"SE",
      "name":"SOS Edital",
      "projectTypeKey":"software",
      "simplified":True,
      "start_date_project": None, 
      "end_date_project":None
   }
    ]

def test_projects_strategy_save_projects_success(db):
    processed =[{
      "jira_id":"10200",
      "uuid":"e915ce14-18fc-417a-92fb",
      "key":"SM2",
      "name":"SOS MNT 2025",
      "projectTypeKey":"software",
      "simplified":True,
      "start_date_project": None,
      "end_date_project":None
   },
   {
      "jira_id":"10202",
      "uuid":"950c63a2-e6bb-4e5d-8390",
      "key":"SE",
      "name":"SOS Edital",
      "projectTypeKey":"software",
      "simplified":True,
      "start_date_project": None,
      "end_date_project": None
   }
    ] 

    strategy = ProjectsApiStrategy('test@example.com', 'token123', 'https://jira.example.com')
    success, msg = strategy.save_projects(processed)
    assert success is True
    assert "Successfully saved 2 projects." in msg

@patch("jiboia.core.service.projects_svc.save_projects")
def test_projects_strategy_save_projects_exception(mock_save_projects, db):
    processed =[{
      "jira_id":"10200",
      "uuid":"950c63a2-e6bb-4e5d-8390",
      "key":"SM2",
      "name":"SOS MNT 2025",
      "projectTypeKey":"software",
      "simplified":True,
      "start_date_project":None,
      "end_date_project": None
   },
   {
      "jira_id":"10202",
      "uuid":"950c63a2-e6bb-4e5d-8390",
      "key":"SE",
      "name":"SOS Edital",
      "projectTypeKey":"software",
      "simplified":True,
      "start_date_project":None,
      "end_date_project": None
   }
    ]     
    mock_save_projects.side_effect = Exception("DB error")
    strategy = ProjectsApiStrategy('test@example.com', 'token123', 'https://jira.example.com')
    success, msg = strategy.save_projects(processed)
    assert success is False
    assert "DB error" in msg