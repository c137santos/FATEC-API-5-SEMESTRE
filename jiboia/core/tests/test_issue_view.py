import json
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.urls import reverse

from jiboia.core.models import Issue, IssueType, Project, StatusType
from jiboia.core.views import add_issue

TEST_PROJECT_ID = 123
DEFAULT_PER_PAGE = 10


@pytest.fixture
def authenticated_user():
    """Creates an authenticated user"""
    user = get_user_model()
    return user.objects.create_user("testuser", "test@example.com", "testpass")


@pytest.fixture
def authenticated_client(client, authenticated_user):
    """Creates a client with an authenticated user"""
    client.force_login(authenticated_user)
    return client


@pytest.mark.django_db
def test_add_issue_success_201(authenticated_client):
    """Tests if the endpoint returns 201 when the issue is successfully created"""
    url = reverse("add_issue")
    issue_data = {"description": "Nova issue de teste válida"}

    with patch("jiboia.core.views.issues_svc.add_issue") as mock_add_issue:
        mock_add_issue.return_value = {
            "id": 1,
            "description": "Nova issue de teste válida",
            "status": None,
            "created_at": "2024-01-01T10:00:00",
        }

        response = authenticated_client.post(url, data=json.dumps(issue_data), content_type="application/json")

        assert response.status_code == 201
        mock_add_issue.assert_called_once_with("Nova issue de teste válida")

        response_data = json.loads(response.content)
        assert response_data["id"] == 1
        assert response_data["description"] == "Nova issue de teste válida"


@pytest.mark.django_db
def test_add_issue_empty_description_400_direct(authenticated_user):
    """Tests empty description directly in the view"""
    from jiboia.core.views import add_issue

    factory = RequestFactory()
    issue_data = {"description": ""}

    request = factory.post("/issues", data=json.dumps(issue_data), content_type="application/json")
    request.user = authenticated_user

    with pytest.raises(ValueError) as exc_info:
        add_issue(request)

    assert "Field required" in str(exc_info.value)


@pytest.mark.django_db
def test_add_issue_invalid_type_description_400_direct(authenticated_user):
    """Tests invalid type directly in the view"""
    from jiboia.core.views import add_issue

    factory = RequestFactory()
    issue_data = {"description": 123}

    request = factory.post("/issues", data=json.dumps(issue_data), content_type="application/json")
    request.user = authenticated_user

    with pytest.raises(ValueError) as exc_info:
        add_issue(request)

    assert "Input should be a valid string" in str(exc_info.value)


@pytest.mark.django_db
def test_add_issue_unauthorized():
    """Tests if it returns 401 when the user is not authenticated"""

    factory = RequestFactory()
    issue_data = {"description": "Teste"}

    request = factory.post("/issues", data=json.dumps(issue_data), content_type="application/json")
    request.user = AnonymousUser()

    response = add_issue(request)
    assert response.status_code == 401


@pytest.mark.django_db
def test_list_paginable_issues_success(client):
    """
    Tests if the list_paginable_issues endpoint successfully returns 200
    with real paginated data.
    """
    issue_type = IssueType.objects.create(name="Tarefa", jira_id=1)
    status_type = StatusType.objects.create(name="Aberto", jira_id=1)
    project = Project.objects.create(id=TEST_PROJECT_ID, name="Projeto Teste", description="", jira_id=1)

    for i in range(15):
        Issue.objects.create(
            description=f"Issue {i}",
            jira_id=i + 1,
            type_issue=issue_type,
            status=status_type,
            project=project,
            time_estimate_seconds=7200,
        )

    url = reverse("list_paginable_issues", kwargs={"project_id": TEST_PROJECT_ID})

    response = client.get(url)

    assert response.status_code == 200

    data = json.loads(response.content)
    assert "issues" in data
    assert "current_page" in data
    assert "total_pages" in data
    assert "total_items" in data
    assert data["total_items"] == 15
    assert len(data["issues"]) == 10
    assert data["issues"][0]["description"] == "Issue 14"


@pytest.mark.django_db
def test_list_paginable_issues_with_invalid_page_parameter_string(client):
    """
    Tests if the endpoint handles an invalid page parameter (string) and defaults to page 1.
    """
    issue_type = IssueType.objects.create(name="Tarefa", jira_id=1)
    status_type = StatusType.objects.create(name="Aberto", jira_id=1)
    project = Project.objects.create(id=TEST_PROJECT_ID, name="Projeto Teste", description="", jira_id=1)
    Issue.objects.create(description="Teste", jira_id=1, type_issue=issue_type, status=status_type, project=project)

    url = reverse("list_paginable_issues", kwargs={"project_id": TEST_PROJECT_ID})

    response = client.get(f"{url}?page=abc")

    assert response.status_code == 200

    data = json.loads(response.content)
    assert data["current_page"] == 1


@pytest.mark.django_db
def test_list_paginable_issues_empty_database(client):
    """
    Tests if the endpoint returns 200 when there are no issues
    """
    Project.objects.create(id=TEST_PROJECT_ID, name="Projeto Vazio", description="", jira_id=1)

    url = reverse("list_paginable_issues", kwargs={"project_id": TEST_PROJECT_ID})

    response = client.get(url)

    assert response.status_code == 200

    data = json.loads(response.content)
    assert data["issues"] == []
    assert data["total_items"] == 0
