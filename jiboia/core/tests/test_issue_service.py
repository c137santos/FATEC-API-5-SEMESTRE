import pytest

from unittest.mock import patch

from jiboia.core.models import Issue
from jiboia.core.service.issues_svc import list_issues

@pytest.mark.django_db
def test_list_paginable_issues_success():
    for i in range(15):
        Issue.objects.create(description=f"Issue {i}", jira_id=i+1)

    result_page1 = list_issues(page_number=1)

    assert result_page1["current_page"] == 1
    assert result_page1["total_pages"] == 2
    assert result_page1["total_items"] == 15
    assert len(result_page1["issues"]) == 10  
    assert result_page1["issues"][0]["description"] == "Issue 14"

    result_page2 = list_issues(page_number=2)
   
    assert result_page2["current_page"] == 2
    assert result_page2["total_pages"] == 2
    assert result_page2["total_items"] == 15
    assert len(result_page2["issues"]) == 5  
    assert result_page2["issues"][0]["description"] == "Issue 4"

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
