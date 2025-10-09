from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model

from jiboia.core.models import Issue, IssueType, Project, StatusType
from jiboia.core.service.issues_svc import add_issue, list_issues


@pytest.mark.django_db
def test_add_issue_success():
    """Testa se a issue foi cadastrada com sucesso"""
    test_description = "Nova issue de teste"
    
    with patch('jiboia.core.service.issues_svc.Issue') as MockIssue:
        mock_issue_instance = MagicMock()
        mock_issue_instance.to_dict_json.return_value = {
            "id": 1,
            "description": test_description
        }
        MockIssue.return_value = mock_issue_instance
        
        result = add_issue(test_description)
        
        MockIssue.assert_called_once_with(description=test_description)
        
        mock_issue_instance.save.assert_called_once()
        
        mock_issue_instance.to_dict_json.assert_called_once()
        
        assert result['id'] == 1
        assert result['description'] == test_description

@pytest.mark.django_db
def test_add_issue_fails_with_empty_description():
    """Testa que falha o cadastro quando descrição é vazia"""
    with pytest.raises(Exception) as exc_info:
        add_issue("")
    
    assert "Invalid description" in str(exc_info.value)

@pytest.mark.django_db
def test_list_paginable_issues_no_user():
    issue_type = IssueType.objects.create(
        name="Tarefa",
        jira_id=1  
    )
    status_type = StatusType.objects.create(
        name="Aberto",
        jira_id=1 
    )
    project = Project.objects.create(
        name="Projeto Teste", 
        description="Descrição teste",
        jira_id=1
    )
    
    for i in range(15):
        Issue.objects.create(
            description=f"Issue {i}", 
            jira_id=i+1,
            type_issue=issue_type,
            status=status_type,
            project=project,
            time_estimate_seconds=7200 
        )

    result_page1 = list_issues(page_number=1)

    assert result_page1["current_page"] == 1
    assert result_page1["total_pages"] == 2
    assert result_page1["total_items"] == 15
    assert len(result_page1["issues"]) == 10
    
    first_issue = result_page1["issues"][0]
    assert "jira_id" in first_issue
    assert "user_related" in first_issue
    assert "time_spend_hours" in first_issue
    assert first_issue["time_spend_hours"] == 2  
    
    assert first_issue["description"] == "Issue 14"
    assert first_issue["jira_id"] == 15

    result_page2 = list_issues(page_number=2)
   
    assert result_page2["current_page"] == 2
    assert result_page2["total_pages"] == 2
    assert result_page2["total_items"] == 15
    assert len(result_page2["issues"]) == 5
    
    first_issue_page2 = result_page2["issues"][0]
    assert first_issue_page2["description"] == "Issue 4"
    assert first_issue_page2["jira_id"] == 5
    assert first_issue_page2["time_spend_hours"] == 2

@pytest.mark.django_db
def test_list_paginable_issues_with_user():    
    user = get_user_model()
    
    test_user = user.objects.create_user(
        username='testuser',
        password='testpass123',
        first_name='Carlos',
        last_name='Oliveira'
    )
    
    issue_type = IssueType.objects.create(name="Tarefa", jira_id=1)
    status_type = StatusType.objects.create(name="Aberto", jira_id=1)
    project = Project.objects.create(name="Projeto Teste", description="Teste", jira_id=1)
    
    Issue.objects.create(
        description="Issue com usuário", 
        jira_id=100,
        type_issue=issue_type,
        status=status_type,
        project=project,
        time_estimate_seconds=3600,
        id_user=test_user 
    )

    result = list_issues(page_number=1)

    assert result["total_items"] == 1
    assert len(result["issues"]) == 1
    
    issue_user_data = result["issues"][0]
    
    assert issue_user_data is not None
    assert issue_user_data["user_related"] is not None
    assert issue_user_data["user_related"]["id"] == test_user.id
    assert issue_user_data["user_related"]["user_name"] == "Carlos Oliveira"
    assert issue_user_data["time_spend_hours"] == 1

@pytest.mark.django_db
def test_list_paginable_issues_failed():
    with patch("jiboia.core.service.issues_svc.Paginator") as mock_paginator:
        mock_instance = mock_paginator.return_value
        mock_instance.page.side_effect = Exception("Erro simulado")  
        mock_instance.num_pages = 3
        mock_instance.count = 25

        result = list_issues(page_number=2)

        assert result["issues"] == []
        assert result["current_page"] == 2
        assert result["total_pages"] == 3
