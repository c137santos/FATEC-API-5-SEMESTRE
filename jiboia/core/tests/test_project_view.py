import json

import pytest
from django.urls import reverse
from django.utils import timezone

from jiboia.core.models import Issue, IssueType, Project, StatusType


@pytest.fixture
def setup_project_data():
    """
    Configura dados de teste para os testes da view de project_overview
    """
    project = Project.objects.create(
        key='TEST',
        name='Projeto de Teste View',
        description='Projeto para testes da view',
        jira_id=501,
        uuid='test-view-uuid',
        projectTypeKey='software'
    )
    
    pending_status = StatusType.objects.create(key='pending', name='Pendente', jira_id=601)
    in_progress_status = StatusType.objects.create(key='in_progress', name='Em Andamento', jira_id=602)
    
    task_type = IssueType.objects.create(name='Task', description='Tarefa', jira_id=701)
    
    Issue.objects.create(
        description='Issue de teste 1',
        project=project,
        status=pending_status,
        type_issue=task_type,
        created_at=timezone.now()
    )
    
    Issue.objects.create(
        description='Issue de teste 2',
        project=project,
        status=in_progress_status,
        type_issue=task_type,
        created_at=timezone.now()
    )
    
    return project

@pytest.mark.django_db
def test_list_projects_general_success_200(client):
    """
    Testa se o endpoint list_projects_general retorna 200 com sucesso
    """
    url = reverse('list_projects_general')
    
    response = client.get(url)
    
    assert response.status_code == 200
    
    data = json.loads(response.content)

    assert isinstance(data, dict)
    assert 'projects' in data
    assert 'issues_per_month' in data
    assert isinstance(data['projects'], list)
    assert isinstance(data['issues_per_month'], list)


@pytest.mark.django_db
def test_list_projects_general_with_valid_parameter(client):
    """
    Testa se o endpoint aceita e processa o parâmetro issues_breakdown_months válido
    """
    url = reverse('list_projects_general')
    
    response = client.get(f'{url}?issues_breakdown_months=3')
    
    assert response.status_code == 200
    
    data = json.loads(response.content)
    assert isinstance(data, dict)
    assert 'projects' in data
    assert 'issues_per_month' in data

@pytest.mark.django_db
def test_list_projects_general_with_invalid_parameter(client):
    """
    Testa se o endpoint trata parâmetro issues_breakdown_months negativo
    """
    url = reverse('list_projects_general')
    
    response = client.get(f'{url}?issues_breakdown_months=-1')
    
    assert response.status_code == 200
    
    data = json.loads(response.content)
    assert isinstance(data, dict)
    assert 'projects' in data

@pytest.mark.django_db
def test_list_projects_general_empty_database(client):
    """
    Testa se o endpoint retorna 200 quando não há projetos
    """
    url = reverse('list_projects_general')
    
    response = client.get(url)
    
    assert response.status_code == 200
    
    data = json.loads(response.content)
    assert isinstance(data, dict)
    assert 'projects' in data
    assert 'issues_per_month' in data
    assert data['projects'] == []  

@pytest.mark.django_db
def test_list_projects_general_structure_validation(client):
    """
    Testa a estrutura completa da resposta
    """
    url = reverse('list_projects_general')
    
    response = client.get(url)
    
    assert response.status_code == 200
    
    data = json.loads(response.content)
    
    assert isinstance(data, dict)
    assert 'projects' in data
    assert 'issues_per_month' in data
    
    if data['projects']:
        project = data['projects'][0]
        assert 'project_id' in project
        assert 'name' in project
        assert 'dev_hours' in project
        assert 'total_hours' in project
    
    if data['issues_per_month']:
        month_data = data['issues_per_month'][0]
        assert 'date' in month_data