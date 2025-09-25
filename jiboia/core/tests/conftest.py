import pytest
from datetime import date
from unittest.mock import patch, MagicMock
from jiboia.core.models import Project

MOCK_TODAY = date(2025, 9, 24)

@pytest.fixture
def mock_today():
    with patch("jiboia.core.service.project_svc.date") as mock_date:
        mock_date.today.return_value = MOCK_TODAY
        mock_date.side_effect = lambda *args, **kwargs: date(*args, **kwargs)
        yield mock_date

@pytest.fixture
def mock_project():
    class MockProject:
        def __init__(self, id, project_id):
            self.id = id
            self.project_id = project_id

        def to_dict_json(self):
            return {"id": self.id, "project_id": self.project_id, "type": "BUG"}
    return MockProject

@pytest.fixture
def mock_project_objects():
    with patch("jiboia.core.models.Project.objects") as mock_manager:
        mock_queryset = MagicMock()
        mock_manager.filter.return_value = mock_queryset
        yield mock_manager, mock_queryset

@pytest.fixture
def mock_issue():
    class MockIssue:
        def __init__(self, id, project_id):
            self.id = id
            self.project_id = project_id

        def to_dict_json(self):
            return {"id": self.id, "project_id": self.project_id, "type": "BUG"}
    return MockIssue
