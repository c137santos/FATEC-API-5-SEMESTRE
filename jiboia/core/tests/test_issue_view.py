import json
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.urls import reverse

from jiboia.core.views import add_issue


@pytest.fixture
def authenticated_user():
    """Cria um usuário autenticado"""
    user = get_user_model()
    return user.objects.create_user('testuser', 'test@example.com', 'testpass')


@pytest.fixture
def authenticated_client(client, authenticated_user):
    """Cria um cliente com usuário autenticado"""
    client.force_login(authenticated_user)
    return client


@pytest.mark.django_db
def test_add_issue_success_201(authenticated_client):
    """Testa se o endpoint retorna 201 quando a issue é criada com sucesso"""
    url = reverse('add_issue')
    issue_data = {
        "description": "Nova issue de teste válida"
    }
    
    with patch('jiboia.core.views.issues_svc.add_issue') as mock_add_issue:
        mock_add_issue.return_value = {
            "id": 1,
            "description": "Nova issue de teste válida",
            "status": None,
            "created_at": "2024-01-01T10:00:00"
        }
        
        response = authenticated_client.post(
            url,
            data=json.dumps(issue_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        mock_add_issue.assert_called_once_with("Nova issue de teste válida")
        
        response_data = json.loads(response.content)
        assert response_data['id'] == 1
        assert response_data['description'] == "Nova issue de teste válida"

@pytest.mark.django_db
def test_add_issue_empty_description_400_direct(authenticated_user):
    """Testa description vazia diretamente na view"""
    from jiboia.core.views import add_issue
    
    factory = RequestFactory()
    issue_data = {"description": ""} 
    
    request = factory.post(
        '/issues',
        data=json.dumps(issue_data),
        content_type='application/json'
    )
    request.user = authenticated_user
    
    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        add_issue(request)
    
    assert "Field required" in str(exc_info.value)

@pytest.mark.django_db
def test_add_issue_invalid_type_description_400_direct(authenticated_user):
    """Testa tipo inválido diretamente na view"""
    from jiboia.core.views import add_issue
    
    factory = RequestFactory()
    issue_data = {"description": 123} 
    
    request = factory.post(
        '/issues',
        data=json.dumps(issue_data),
        content_type='application/json'
    )
    request.user = authenticated_user
    
    with pytest.raises(ValueError) as exc_info:
        add_issue(request)
    
    assert "Input should be a valid string" in str(exc_info.value)


@pytest.mark.django_db
def test_add_issue_unauthorized():
    """Testa se retorna 401 quando usuário não está autenticado"""

    factory = RequestFactory()
    issue_data = {"description": "Teste"}
    
    request = factory.post(
        '/issues',
        data=json.dumps(issue_data),
        content_type='application/json'
    )
    request.user = AnonymousUser()  
    
    response = add_issue(request)
    assert response.status_code == 401


@pytest.mark.django_db
def test_list_paginable_issues_success(client):
    """
    Testa se o endpoint list_paginable_issues retorna 200 com sucesso
    """
    url = reverse('list_paginable_issues')
    response = client.get(url)
    
    assert response.status_code == 200
    
    data = json.loads(response.content)
    assert 'issues' in data
    assert 'current_page' in data
    assert 'total_pages' in data
    assert 'total_items' in data


@pytest.mark.django_db
def test_list_paginable_issues_with_invalid_page_parameter_string(client):
    """
    Testa se o endpoint trata parâmetro page inválido (string)
    """
    url = reverse('list_paginable_issues')
    response = client.get(f'{url}?page=abc')
    
    assert response.status_code == 200
    
    data = json.loads(response.content)
    assert data['current_page'] == 1


@pytest.mark.django_db
def test_list_paginable_issues_empty_database(client):
    """
    Testa se o endpoint retorna 200 quando não há issues
    """
    url = reverse('list_paginable_issues')
    response = client.get(url)
    
    assert response.status_code == 200
    
    data = json.loads(response.content)
    assert data['issues'] == []
    assert data['total_items'] == 0