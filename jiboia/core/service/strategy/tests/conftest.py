"""Pytest configuration for strategy tests."""

from unittest.mock import MagicMock

import pytest

import jiboia.core.service.strategy.issues as issues_mod
from jiboia.core.models import Project as RealProject
from jiboia.core.models import StatusType as RealStatusType
from jiboia.core.service.strategy.issues import SyncIssuesStrategy


class DummyUser:
    def __init__(self, username):
        self.username = username

class DummyIssueType:
    def __init__(self, jira_id):
        self.jira_id = jira_id

class DummyStatusType:
    def __init__(self, jira_id):
        self.jira_id = jira_id

class DummyQuerySetForSync:
    """Simula um QuerySet para issues para o cenário de sincronização."""
    def all(self):
        return self
        
    def aggregate(self, *args, **kwargs):
        return {
            "start_date__min": None,
            "end_date__max": None,
        }


class DummyProjectForSync:
    def __init__(self, key="PRJ"):
        self.key = key
        self.start_date_project = None
        self.end_date_project = None
        self.saved = False
        self.issue_set = DummyQuerySetForSync() 

    def save(self):
        self.saved = True

class DummyTimeLog:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class DummyIssue:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.timelog_set = []

class DummyManager:
    def get(self, **kwargs):
        if kwargs.get('jira_id') == '10001':
            return DummyIssueType(jira_id='10001')
        if kwargs.get('jira_id') == '10002':
            return DummyStatusType(jira_id='10002')
        if kwargs.get('key') == 'PRJ':
            return DummyProjectForSync(key='PRJ')
        
        if 'key' in kwargs:
             raise RealProject.DoesNotExist
        if 'jira_id' in kwargs:
             raise RealStatusType.DoesNotExist 

    def update_or_create(self, **kwargs):
        if self is DummyIssue.objects:
            issue = DummyIssue(**kwargs.get('defaults', {}))
            issue.jira_id = kwargs.get('jira_id')
            return issue, True
        
        if self is DummyTimeLog.objects:
            timelog = DummyTimeLog(**kwargs.get('defaults', {}))
            timelog.jira_id = kwargs.get('jira_id')
            return timelog, True
        
        return None, False

DummyIssue.objects = DummyManager()
DummyTimeLog.objects = DummyManager()
DummyIssueType.objects = DummyManager()
DummyStatusType.objects = DummyManager()
DummyProjectForSync.objects = DummyManager()

@pytest.fixture
def jira_user_data():
    """Dados de usuário do Jira simulados."""
    return {"accountId": "user123", "displayName": "Teste User"}

@pytest.fixture
def jira_issue_data_page1(jira_user_data):
    """Payload de uma página com uma issue e worklog simulados."""
    return {
        "total": 1,
        "issues": [
            {
                "id": "10001",
                "key": "PRJ-1",
                "fields": {
                    "summary": "Issue Test",
                    "assignee": jira_user_data,
                    "issuetype": {"id": "10001"},
                    "status": {"id": "10002"},
                    "created": "2023-01-01T10:00:00.000+0000",
                    "resolutiondate": "2023-01-10T10:00:00.000+0000",
                    "timeestimate": 3600,
                    "customfield_10015": "2023-01-01", 
                    "description": {"content": [{"content": [{"text": "Detalhes da Issue"}]}]},
                    "worklog": {
                        "worklogs": [
                            {
                                "id": "100001",
                                "author": jira_user_data,
                                "timeSpentSeconds": 1800,
                                "started": "2023-01-02T10:00:00.000+0000",
                                "comment": {
                                    "content": [
                                        {"type": "paragraph", "content": [{"type": "text", "text": "Worklog Test"}]}
                                    ]
                                },
                            }
                        ]
                    },
                },
            }
        ],
    }

@pytest.fixture
def jira_issue_data_page_empty():
    """Payload de uma página de resultados vazia."""
    return {"total": 1, "issues": []}

@pytest.fixture
def sync_issues_strategy_setup(monkeypatch):
    """
    Configura o ambiente de teste, injetando as classes Dummy nos módulos
    reais e simulando a sincronização de usuário.
    """
    
    def dummy_sync_user_execute(self, user_data, email, token, base_url):
        return DummyUser(user_data["accountId"])

    monkeypatch.setattr(issues_mod, 'Project', DummyProjectForSync)
    monkeypatch.setattr(issues_mod, 'Issue', DummyIssue)
    monkeypatch.setattr(issues_mod, 'TimeLog', DummyTimeLog)
    monkeypatch.setattr(issues_mod, 'IssueType', DummyIssueType)
    monkeypatch.setattr(issues_mod, 'StatusType', DummyStatusType)
    
    monkeypatch.setattr(issues_mod.SyncUserStrategy, 'execute', dummy_sync_user_execute)
    
    monkeypatch.setattr(issues_mod, 'User', DummyUser)

    strategy = SyncIssuesStrategy("email", "token", "http://fake-jira")
    strategy.Project = DummyProjectForSync
    strategy.Issue = DummyIssue
    return strategy

@pytest.fixture
def mock_response():
    """Create a mock response object."""
    response = MagicMock()
    return response


@pytest.fixture
def projects_data():
    """Sample projects data."""
    return [
        {
            "expand": "description,lead,issueTypes,url,projectKeys,permissions,insight",
            "self": "https://fatec/rest/api/3/project/10200",
            "id": "10200",
            "key": "SM2",
            "description": "",
            "lead": {
                "self": "https://fatec/rest/api/3/user?accountId=5e1c75cd5523db0ca669f853",
                "accountId": "5e1c75cd5523db0ca669f853",
                "accountType": "atlassian",
                "avatarUrls": {
                    "48x48": "https://avatar-management--avatars.us-west-2.prod.public.atl-paas.net/initials/VM-3.png",
                },
                "displayName": "Eduardo Sakaue",
                "active": True,
            },
            "issueTypes": [
                {
                    "self": "https://fatec/rest/api/3/issuetype/10551",
                    "id": "10551",
                    "description": "As tarefas monitoram partes pequenas e distintas do trabalho.",
                    "iconUrl": "https://fatec/rest/api/2/universal_avatar/view/type/issuetype/avatar/10318?size=medium",
                    "name": "Tarefa",
                    "subtask": False,
                    "avatarId": 10318,
                    "hierarchyLevel": 0,
                },
                {
                    "self": "https://fatec/rest/api/3/issuetype/10552",
                    "id": "10552",
                    "description": "Os bugs monitoram problemas ou erros.",
                    "iconUrl": "https://fatec/rest/api/2/universal_avatar/view/type/issuetype/avatar/10303?size=medium",
                    "name": "Bug",
                    "subtask": False,
                    "avatarId": 10303,
                    "hierarchyLevel": 0,
                },
                {
                    "self": "https://fatec/rest/api/3/issuetype/10553",
                    "id": "10553",
                    "description": "As histórias monitoram funções ou recursos expressos como objetivos do usuário.",
                    "iconUrl": "https://fatec/rest/api/2/universal_avatar/view/type/issuetype/avatar/10315?size=medium",
                    "name": "História",
                    "subtask": False,
                    "avatarId": 10315,
                    "hierarchyLevel": 0,
                },
                {
                    "self": "https://fatec/rest/api/3/issuetype/10554",
                    "id": "10554",
                    "description": "Os epics monitoram coleções de tarefas, histórias e bugs relacionados.",
                    "iconUrl": "https://fatec/rest/api/2/universal_avatar/view/type/issuetype/avatar/10307?size=medium",
                    "name": "Epic",
                    "subtask": False,
                    "avatarId": 10307,
                    "hierarchyLevel": 1,
                },
                {
                    "self": "https://fatec/rest/api/3/issuetype/10555",
                    "id": "10555",
                    "description": "As subtarefas monitoram pequenas partes do trabalho que fazem parte de uma tarefa.",
                    "iconUrl": "https://fatec/rest/api/2/universal_avatar/view/type/issuetype/avatar/10316?size=medium",
                    "name": "Subtarefa",
                    "subtask": True,
                    "avatarId": 10316,
                    "hierarchyLevel": -1,
                },
            ],
            "name": "SOS MNT 2025",
            "avatarUrls": {
                "48x48": "https://fatec/rest/api/3/universal_avatar/view/type/project/avatar/10423",
            },
            "projectKeys": ["SM2"],
            "projectTypeKey": "software",
            "simplified": True,
            "style": "next-gen",
            "isPrivate": False,
            "properties": {},
            "entityId": "e915ce14-18fc-417a-92fb",
            "uuid": "e915ce14-18fc-417a-92fb",
        },
        {
            "expand": "description,lead,issueTypes,url,projectKeys,permissions,insight",
            "self": "https://fatec/rest/api/3/project/10202",
            "id": "10202",
            "key": "SE",
            "description": "",
            "lead": {
                "self": "https://fatec/rest/api/3/user?accountId=5e1c75cd5523db0ca669f853",
                "accountId": "5e1c75cd5523db0ca669f853",
                "accountType": "atlassian",
                "avatarUrls": {
                    "48x48": "https://avatar-management--avatars.us-west-2.prod.public.atl-paas.net/initials/VM-3.png",
                },
                "displayName": "Eduardo Sakaue",
                "active": True,
            },
            "issueTypes": [
                {
                    "self": "https://fatec/rest/api/3/issuetype/10559",
                    "id": "10559",
                    "description": "As tarefas monitoram partes pequenas e distintas do trabalho.",
                    "iconUrl": "https://fatec/rest/api/2/universal_avatar/view/type/issuetype/avatar/10318?size=medium",
                    "name": "Tarefa",
                    "subtask": False,
                    "avatarId": 10318,
                    "hierarchyLevel": 0,
                },
                {
                    "self": "https://fatec/rest/api/3/issuetype/10560",
                    "id": "10560",
                    "description": "Os epics monitoram coleções de tarefas, histórias e bugs relacionados.",
                    "iconUrl": "https://fatec/rest/api/2/universal_avatar/view/type/issuetype/avatar/10307?size=medium",
                    "name": "Epic",
                    "subtask": False,
                    "avatarId": 10307,
                    "hierarchyLevel": 1,
                },
                {
                    "self": "https://fatec/rest/api/3/issuetype/10561",
                    "id": "10561",
                    "description": "As subtarefas monitoram pequenas partes do trabalho que fazem parte de uma tarefa.",
                    "iconUrl": "https://fatec/rest/api/2/universal_avatar/view/type/issuetype/avatar/10316?size=medium",
                    "name": "Subtarefa",
                    "subtask": True,
                    "avatarId": 10316,
                    "hierarchyLevel": -1,
                },
                {
                    "self": "https://fatec/rest/api/3/issuetype/10625",
                    "id": "10625",
                    "description": "Erros rastreiam problemas ou erros.",
                    "iconUrl": "https://fatec/rest/api/2/universal_avatar/view/type/issuetype/avatar/10303?size=medium",
                    "name": "Erro",
                    "subtask": False,
                    "avatarId": 10303,
                    "hierarchyLevel": 0,
                },
            ],
            "name": "SOS Edital",
            "avatarUrls": {
                "48x48": "https://fatec/rest/api/3/universal_avatar/view/type/project/avatar/10412",
            },
            "projectKeys": ["SE"],
            "projectTypeKey": "software",
            "simplified": True,
            "style": "next-gen",
            "isPrivate": False,
            "properties": {},
            "entityId": "950c63a2-e6bb-4e5d-8390",
            "uuid": "950c63a2-e6bb-4e5d-8390",
        },
    ]