import pytest

from jiboia.core.service.issues_type_svc import list_type_issues

from ..models import IssueType


@pytest.mark.django_db
def test_list_issues_com_dados():
    issue1 = IssueType.objects.create(name="Task", description="Small unit of work", subtask=False, jira_id=10101)
    issue2 = IssueType.objects.create(name="Subtask", description="Part of a larger task", subtask=True, jira_id=10102)

    result = list_type_issues()
    assert len(result) == 2
    assert result[0]["issuetype_id"] == issue1.id
    assert result[0]["name"] == "Task"
    assert result[0]["subtask"] is False
    assert result[1]["issuetype_id"] == issue2.id
    assert result[1]["name"] == "Subtask"
    assert result[1]["subtask"] is True


@pytest.mark.django_db
def test_list_issues_sem_dados():
    result = list_type_issues()
    assert result == []
