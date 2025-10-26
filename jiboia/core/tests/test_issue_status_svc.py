import pytest

from jiboia.core.models import StatusType
from jiboia.core.service.issue_status_svc import list_status_type


@pytest.mark.django_db
def test_list_status_type_com_dados():
    """Testa se a função retorna todos os StatusType no formato serializado correto."""
    status1 = StatusType.objects.create(name="OPEN", jira_id=10001)
    StatusType.objects.create(name="CLOSED", jira_id=10002)
    result = list_status_type()
    assert len(result) == 2
    assert result[0]["statustype_id"] == status1.id
    assert result[0]["name"] == "OPEN"
    assert result[0]["jira_id"] == 10001


@pytest.mark.django_db
def test_list_status_type_sem_dados():
    """Testa se a função retorna uma lista vazia quando não há dados."""
    result = list_status_type()
    assert result == []
