from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest
import requests
from django.contrib.auth import get_user_model
from django.utils import timezone

from jiboia.core.models import Issue, IssueType, Project, StatusType, TimeLog
from jiboia.core.service.strategy.issues import SyncIssuesStrategy


@pytest.mark.django_db
def test_update_project_dates():
    """Tests the update of project dates based on issues"""
    project = Project.objects.create(
        jira_id=12345, key="TEST", name="Test Project", start_date_project=None, end_date_project=None
    )

    Issue.objects.create(
        project=project,
        jira_id=1,
        description="Issue 1",
        start_date=timezone.make_aware(datetime(2023, 1, 1)),
        end_date=timezone.make_aware(datetime(2023, 1, 10)),
    )
    Issue.objects.create(
        project=project,
        jira_id=2,
        description="Issue 2",
        start_date=timezone.make_aware(datetime(2023, 1, 5)),
        end_date=timezone.make_aware(datetime(2023, 1, 20)),
    )
    Issue.objects.create(project=project, jira_id=3, description="Issue 3", start_date=None, end_date=None)

    SyncIssuesStrategy.update_project_dates(project)

    project.refresh_from_db()

    assert project.start_date_project == date(2023, 1, 1)
    assert project.end_date_project == date(2023, 1, 20)


@pytest.mark.django_db
def test_execute_sync_issues_integration():
    """Tests synchronisation of issue with integration"""
    strategy = SyncIssuesStrategy("email", "token", "http://fake-jira")

    project = Project.objects.create(jira_id=12345, key="PRJ", name="Test Project")
    IssueType.objects.create(jira_id=1, name="Bug")
    StatusType.objects.create(jira_id=1, name="To Do")

    mock_data = {
        "total": 1,
        "issues": [
            {
                "id": "10001",
                "fields": {
                    "summary": "Test Issue",
                    "description": None,
                    "assignee": None,
                    "issuetype": {"id": "1"},
                    "status": {"id": "1"},
                    "created": "2023-01-01T00:00:00.000Z",
                    "resolutiondate": None,
                    "customfield_10015": None,
                    "timeestimate": None,
                    "worklog": {"worklogs": []},
                },
            }
        ],
    }

    mock_response_object = MagicMock()
    mock_response_object.json.return_value = mock_data
    mock_response_object.status_code = 200

    with (
        patch("requests.get", return_value=mock_response_object),
        patch("jiboia.core.service.strategy.users.SyncUserStrategy.execute", return_value=None),
    ):
        synced_count = strategy.execute("PRJ")

        assert synced_count == 1

        issue = Issue.objects.get(project=project)
        assert issue.jira_id == 10001
        assert issue.description == "Test Issue"


@pytest.mark.django_db
def test_sync_worklogs_creation():
    """Tests synchronisation of worklogs"""
    strategy = SyncIssuesStrategy("email", "token", "http://fake-jira")

    project = Project.objects.create(jira_id=12345, key="PRJ", name="Test Project")

    issue = Issue.objects.create(project=project, jira_id=10001, description="Test Issue")

    worklog_data = {
        "id": "10001",
        "fields": {
            "worklog": {
                "worklogs": [
                    {
                        "id": "20001",
                        "author": {"accountId": "user123"},
                        "timeSpentSeconds": 7200,
                        "started": "2023-01-01T10:00:00.000Z",
                        "comment": {"content": [{"content": [{"text": "Worklog Test"}]}]},
                    }
                ]
            }
        },
    }

    def mock_sync_user_execute(*args, **kwargs):
        try:
            if args and hasattr(args[0], "get") and callable(getattr(args[0], "get")):
                user_data = args[0]
                account_id = user_data.get("accountId", "user123")
            elif kwargs and "user_data" in kwargs:
                user_data = kwargs["user_data"]
                account_id = user_data.get("accountId", "user123")
            else:
                account_id = "user123"
        except (AttributeError, IndexError, TypeError):
            account_id = "user123"

        user = get_user_model()
        new_user, _ = user.objects.get_or_create(username=account_id, defaults={"email": f"{account_id}@test.com"})
        return new_user

    with patch("jiboia.core.service.strategy.users.SyncUserStrategy.execute", mock_sync_user_execute):
        strategy._sync_worklogs(issue, worklog_data)

        worklog = TimeLog.objects.get(jira_id=20001)
        assert worklog.id_issue == issue
        assert worklog.seconds == 7200
        assert worklog.description_log == "Worklog Test"


@pytest.mark.django_db
def test_sync_issue_without_assignee():
    """Tests synchronisation of issue without assignee"""
    strategy = SyncIssuesStrategy("email", "token", "http://fake-jira")

    project = Project.objects.create(jira_id=12345, key="PRJ", name="Test Project")
    IssueType.objects.create(jira_id=1, name="Bug")
    StatusType.objects.create(jira_id=1, name="To Do")

    issue_data = {
        "id": "10003",
        "fields": {
            "summary": "Issue Without Assignee",
            "description": None,
            "assignee": None,
            "issuetype": {"id": "1"},
            "status": {"id": "1"},
            "created": "2023-01-01T00:00:00.000Z",
            "resolutiondate": None,
            "customfield_10015": None,
            "timeestimate": None,
        },
    }

    mock_sync_user_execute = MagicMock()

    with patch("jiboia.core.service.strategy.users.SyncUserStrategy.execute", mock_sync_user_execute):
        issue_obj = strategy._sync_issue(issue_data, project)

        mock_sync_user_execute.assert_not_called()

        assert issue_obj is not None
        assert int(issue_obj.jira_id) == 10003
        assert issue_obj.description == "Issue Without Assignee"
        assert issue_obj.id_user is None


@pytest.mark.django_db
def test_execute_sync_issues_project_not_found():
    """Tests the behavior when the project does not exist in the database"""
    strategy = SyncIssuesStrategy("email", "token", "http://fake-jira")

    synced_count = strategy.execute("NONEXISTENT")

    assert synced_count == 0


@pytest.mark.django_db
def test_execute_sync_issues_with_network_error():
    """Tests error handling when the Jira API is unavailable"""
    strategy = SyncIssuesStrategy("email", "token", "http://fake-jira")

    project = Project.objects.create(jira_id=12345, key="PRJ", name="Test Project")

    def mock_requests_get(url, params=None, auth=None, timeout=None):
        raise requests.exceptions.ConnectionError("Cannot connect to Jira API")

    with patch("requests.get", mock_requests_get):
        with pytest.raises(requests.exceptions.ConnectionError):
            strategy.execute("PRJ")

        assert Issue.objects.filter(project=project).count() == 0


@pytest.mark.django_db
def test_sync_issue_multiples_worklogs():
    strategy = SyncIssuesStrategy("email", "token", "http://fake-jira")

    project = Project.objects.create(jira_id=12345, key="PRJ", name="Test Project")

    issue = Issue.objects.create(project=project, jira_id=66666, description="Test Issue")

    worklog_data = {
        "expand": "renderedFields,names,schema,operations,editmeta,changelog,versionedRepresentations",
        "id": "25265",
        "self": "https://fake.atlassian.net/rest/api/3/issue/25265",
        "key": "SM2-92",
        "changelog": {
            "startAt": 0,
            "maxResults": 5,
            "total": 5,
            "histories": [
                {
                    "id": "125093",
                    "author": {
                        "self": "https://fake.atlassian.net/rest/api/3/user?accountId=5e1c75cd5523db0ca669f853",
                        "accountId": "5e1c75cd5523db0ca669f853",
                        "avatarUrls": {},
                        "displayName": "Vanessa Matsumura",
                        "active": True,
                        "timeZone": "America/Sao_Paulo",
                        "accountType": "atlassian",
                    },
                    "created": "2025-10-16T12:54:42.563-0300",
                    "items": [
                        {
                            "field": "IssueParentAssociation",
                            "fieldtype": "jira",
                            "from": None,
                            "fromString": None,
                            "to": "24790",
                            "toString": "SM2-89",
                        }
                    ],
                },
                {
                    "id": "125079",
                    "author": {
                        "self": "https://fake.atlassian.net/rest/api/3/user?accountId=624c9b884fe01d006baa37e4",
                        "accountId": "624c9b884fe01d006baa37e4",
                        "avatarUrls": {},
                        "displayName": "sergio.casas",
                        "active": True,
                        "timeZone": "America/Sao_Paulo",
                        "accountType": "atlassian",
                    },
                    "created": "2025-10-16T11:38:38.319-0300",
                    "items": [
                        {
                            "field": "WorklogId",
                            "fieldtype": "jira",
                            "from": None,
                            "fromString": None,
                            "to": "48028",
                            "toString": "48028",
                        },
                        {
                            "field": "timeestimate",
                            "fieldtype": "jira",
                            "fieldId": "timeestimate",
                            "from": "0",
                            "fromString": "0",
                            "to": "0",
                            "toString": "0",
                        },
                        {
                            "field": "timespent",
                            "fieldtype": "jira",
                            "fieldId": "timespent",
                            "from": "3600",
                            "fromString": "3600",
                            "to": "7200",
                            "toString": "7200",
                        },
                    ],
                },
                {
                    "id": "125078",
                    "author": {
                        "self": "https://fake.atlassian.net/rest/api/3/user?accountId=624c9b884fe01d006baa37e4",
                        "accountId": "624c9b884fe01d006baa37e4",
                        "avatarUrls": {},
                        "displayName": "sergio.casas",
                        "active": True,
                        "timeZone": "America/Sao_Paulo",
                        "accountType": "atlassian",
                    },
                    "created": "2025-10-16T11:38:20.658-0300",
                    "items": [
                        {
                            "field": "timeestimate",
                            "fieldtype": "jira",
                            "fieldId": "timeestimate",
                            "from": None,
                            "fromString": None,
                            "to": "0",
                            "toString": "0",
                        },
                        {
                            "field": "timespent",
                            "fieldtype": "jira",
                            "fieldId": "timespent",
                            "from": None,
                            "fromString": None,
                            "to": "3600",
                            "toString": "3600",
                        },
                        {
                            "field": "WorklogId",
                            "fieldtype": "jira",
                            "from": None,
                            "fromString": None,
                            "to": "48027",
                            "toString": "48027",
                        },
                    ],
                },
                {
                    "id": "125077",
                    "author": {
                        "self": "https://fake.atlassian.net/rest/api/3/user?accountId=624c9b884fe01d006baa37e4",
                        "accountId": "624c9b884fe01d006baa37e4",
                        "avatarUrls": {},
                        "displayName": "sergio.casas",
                        "active": True,
                        "timeZone": "America/Sao_Paulo",
                        "accountType": "atlassian",
                    },
                    "created": "2025-10-16T11:38:05.896-0300",
                    "items": [
                        {
                            "field": "summary",
                            "fieldtype": "jira",
                            "fieldId": "summary",
                            "from": None,
                            "fromString": "reunião cliente",
                            "to": None,
                            "toString": "reunião cliente outubro 2025",
                        }
                    ],
                },
                {
                    "id": "125076",
                    "author": {
                        "self": "https://fake.atlassian.net/rest/api/3/user?accountId=624c9b884fe01d006baa37e4",
                        "accountId": "624c9b884fe01d006baa37e4",
                        "avatarUrls": {},
                        "displayName": "sergio.casas",
                        "active": True,
                        "timeZone": "America/Sao_Paulo",
                        "accountType": "atlassian",
                    },
                    "created": "2025-10-16T11:37:52.196-0300",
                    "items": [
                        {
                            "field": "Sprint",
                            "fieldtype": "custom",
                            "fieldId": "customfield_10020",
                            "from": "",
                            "fromString": "",
                            "to": "1405",
                            "toString": "Outubro",
                        }
                    ],
                },
            ],
        },
        "fields": {
            "statuscategorychangedate": "2025-10-16T11:37:51.743-0300",
            "issuetype": {
                "self": "https://fake.atlassian.net/rest/api/3/issuetype/10551",
                "id": "10551",
                "description": "As tarefas monitoram partes pequenas e distintas do trabalho.",
                "iconUrl": "https://fake.atlassian.net/rest/api/2/universal_avatar/view/type/issuetype/avatar/10318?size=medium",
                "name": "Tarefa",
                "subtask": False,
                "avatarId": 10318,
                "entityId": "011c6ee0-0457-40b4-97bc-19f851580d00",
                "hierarchyLevel": 0,
            },
            "parent": {
                "id": "24790",
                "key": "SM2-89",
                "self": "https://fake.atlassian.net/rest/api/3/issue/24790",
                "fields": {
                    "summary": "Outubro",
                    "status": {
                        "self": "https://fake.atlassian.net/rest/api/3/status/10772",
                        "description": "",
                        "iconUrl": "https://fake.atlassian.net/",
                        "name": "Tarefas pendentes",
                        "id": "10772",
                        "statusCategory": {
                            "self": "https://fake.atlassian.net/rest/api/3/statuscategory/2",
                            "id": 2,
                            "key": "new",
                            "colorName": "blue-gray",
                            "name": "Itens Pendentes",
                        },
                    },
                    "priority": {
                        "self": "https://fake.atlassian.net/rest/api/3/priority/3",
                        "iconUrl": "https://fake.atlassian.net/images/icons/priorities/medium_new.svg",
                        "name": "Medium",
                        "id": "3",
                    },
                    "issuetype": {
                        "self": "https://fake.atlassian.net/rest/api/3/issuetype/10554",
                        "id": "10554",
                        "description": "Os epics monitoram coleções de tarefas, histórias e bugs relacionados.",
                        "iconUrl": "https://fake.atlassian.net/rest/api/2/universal_avatar/view/type/issuetype/avatar/10307?size=medium",
                        "name": "Epic",
                        "subtask": False,
                        "avatarId": 10307,
                        "entityId": "9a2a6f10-3f7c-4bd0-a56b-e09563344107",
                        "hierarchyLevel": 1,
                    },
                },
            },
            "components": [],
            "timespent": 7200,
            "timeoriginalestimate": None,
            "project": {
                "self": "https://fake.atlassian.net/rest/api/3/project/10200",
                "id": "10200",
                "key": "SM2",
                "name": "SOS MNT 2025",
                "projectTypeKey": "software",
                "simplified": True,
                "avatarUrls": {},
            },
            "description": None,
            "fixVersions": [],
            "aggregatetimespent": 7200,
            "statusCategory": {
                "self": "https://fake.atlassian.net/rest/api/3/statuscategory/2",
                "id": 2,
                "key": "new",
                "colorName": "blue-gray",
                "name": "Itens Pendentes",
            },
            "resolution": None,
            "timetracking": {
                "remainingEstimate": "0h",
                "timeSpent": "2h",
                "remainingEstimateSeconds": 0,
                "timeSpentSeconds": 7200,
            },
            "customfield_10015": None,
            "security": None,
            "attachment": [],
            "aggregatetimeestimate": 0,
            "resolutiondate": None,
            "workratio": -1,
            "summary": "reunião cliente outubro 2025",
            "issuerestriction": {"issuerestrictions": {}, "shouldDisplay": True},
            "watches": {
                "self": "https://fake.atlassian.net/rest/api/3/issue/SM2-92/watchers",
                "watchCount": 1,
                "isWatching": False,
            },
            "lastViewed": None,
            "creator": {
                "self": "https://fake.atlassian.net/rest/api/3/user?accountId=624c9b884fe01d006baa37e4",
                "accountId": "624c9b884fe01d006baa37e4",
                "avatarUrls": {},
                "displayName": "sergio.casas",
                "active": True,
                "timeZone": "America/Sao_Paulo",
                "accountType": "atlassian",
            },
            "subtasks": [],
            "created": "2025-10-16T11:37:51.518-0300",
            "customfield_10020": [
                {
                    "id": 1405,
                    "name": "Outubro",
                    "state": "active",
                    "boardId": 135,
                    "goal": "",
                    "startDate": "2025-10-01T12:08:06.137Z",
                    "endDate": "2025-10-31T12:08:00.000Z",
                }
            ],
            "customfield_10021": None,
            "reporter": {
                "self": "https://fake.atlassian.net/rest/api/3/user?accountId=624c9b884fe01d006baa37e4",
                "accountId": "624c9b884fe01d006baa37e4",
                "avatarUrls": {},
                "displayName": "sergio.casas",
                "active": True,
                "timeZone": "America/Sao_Paulo",
                "accountType": "atlassian",
            },
            "aggregateprogress": {"progress": 7200, "total": 7200, "percent": 100},
            "priority": {
                "self": "https://fake.atlassian.net/rest/api/3/priority/3",
                "iconUrl": "https://fake.atlassian.net/images/icons/priorities/medium_new.svg",
                "name": "Medium",
                "id": "3",
            },
            "customfield_10001": None,
            "labels": [],
            "customfield_10016": None,
            "environment": None,
            "customfield_10019": "0|i019it:",
            "timeestimate": 0,
            "aggregatetimeoriginalestimate": None,
            "versions": [],
            "duedate": None,
            "progress": {"progress": 7200, "total": 7200, "percent": 100},
            "issuelinks": [],
            "votes": {
                "self": "https://fake.atlassian.net/rest/api/3/issue/SM2-92/votes",
                "votes": 0,
                "hasVoted": False,
            },
            "comment": {
                "comments": [],
                "self": "https://fake.atlassian.net/rest/api/3/issue/25265/comment",
                "maxResults": 0,
                "total": 0,
                "startAt": 0,
            },
            "assignee": None,
            "worklog": {
                "startAt": 0,
                "maxResults": 20,
                "total": 2,
                "worklogs": [
                    {
                        "self": "https://fake.atlassian.net/rest/api/3/issue/25265/worklog/48028",
                        "author": {
                            "self": "https://fake.atlassian.net/rest/api/3/user?accountId=624c9b884fe01d006baa37e4",
                            "accountId": "xxxxxx",
                            "avatarUrls": {},
                            "displayName": "sergio.casas",
                            "active": True,
                            "timeZone": "America/Sao_Paulo",
                            "accountType": "atlassian",
                        },
                        "updateAuthor": {
                            "self": "https://fake.atlassian.net/rest/api/3/user?accountId=624c9b884fe01d006baa37e4",
                            "accountId": "xxxxxx",
                            "avatarUrls": {},
                            "displayName": "sergio.casas",
                            "active": True,
                            "timeZone": "America/Sao_Paulo",
                            "accountType": "atlassian",
                        },
                        "created": "2025-10-16T11:38:38.302-0300",
                        "updated": "2025-10-16T11:38:38.302-0300",
                        "started": "2025-10-10T15:00:00.000-0300",
                        "timeSpent": "1h",
                        "timeSpentSeconds": 3600,
                        "id": "66666",
                        "issueId": "66666",
                    },
                    {
                        "self": "https://fake.atlassian.net/rest/api/3/issue/25265/worklog/48027",
                        "author": {
                            "self": "https://fake.atlassian.net/rest/api/3/user?accountId=xxxxx",
                            "accountId": "xxxx",
                            "avatarUrls": {},
                            "displayName": "sergio.casas",
                            "active": True,
                            "timeZone": "America/Sao_Paulo",
                            "accountType": "atlassian",
                        },
                        "updateAuthor": {
                            "self": "https://fake.atlassian.net/rest/api/3/user?accountId=xxxxx",
                            "accountId": "xxxxx",
                            "avatarUrls": {},
                            "displayName": "sergio.casas",
                            "active": True,
                            "timeZone": "America/Sao_Paulo",
                            "accountType": "atlassian",
                        },
                        "created": "2025-10-16T11:38:20.641-0300",
                        "updated": "2025-10-16T11:38:20.641-0300",
                        "started": "2025-10-15T15:00:00.000-0300",
                        "timeSpent": "1h",
                        "timeSpentSeconds": 3600,
                        "id": "55555",
                        "issueId": "66666",
                    },
                ],
            },
            "updated": "2025-10-16T12:54:42.563-0300",
            "status": {
                "self": "https://fake.atlassian.net/rest/api/3/status/10772",
                "description": "",
                "iconUrl": "https://fake.atlassian.net/",
                "name": "Tarefas pendentes",
                "id": "10772",
                "statusCategory": {
                    "self": "https://fake.atlassian.net/rest/api/3/statuscategory/2",
                    "id": 2,
                    "key": "new",
                    "colorName": "blue-gray",
                    "name": "Itens Pendentes",
                },
            },
        },
    }

    def mock_sync_user_execute(*args, **kwargs):
        try:
            if args and hasattr(args[0], "get") and callable(getattr(args[0], "get")):
                user_data = args[0]
                account_id = user_data.get("accountId", "user123")
            elif kwargs and "user_data" in kwargs:
                user_data = kwargs["user_data"]
                account_id = user_data.get("accountId", "user123")
            else:
                account_id = "user123"
        except (AttributeError, IndexError, TypeError):
            account_id = "user123"

        user = get_user_model()
        new_user, _ = user.objects.get_or_create(username=account_id, defaults={"email": f"{account_id}@test.com"})
        return new_user

    with patch("jiboia.core.service.strategy.users.SyncUserStrategy.execute", mock_sync_user_execute):
        strategy._sync_worklogs(issue, worklog_data)

        worklog = TimeLog.objects.get(jira_id=66666)
        assert worklog.id_issue == issue
        assert worklog.seconds == 3600
        assert worklog.description_log == ""
        TimeLog.objects.get(jira_id=55555)
        assert worklog.id_issue == issue
        assert worklog.seconds == 3600
        assert worklog.description_log == ""
