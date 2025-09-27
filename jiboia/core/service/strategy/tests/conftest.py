"""Pytest configuration for strategy tests."""

from unittest.mock import MagicMock

import pytest


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
            "active": True
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
                "hierarchyLevel": 0
            },
            {
                "self": "https://fatec/rest/api/3/issuetype/10552",
                "id": "10552",
                "description": "Os bugs monitoram problemas ou erros.",
                "iconUrl": "https://fatec/rest/api/2/universal_avatar/view/type/issuetype/avatar/10303?size=medium",
                "name": "Bug",
                "subtask": False,
                "avatarId": 10303,
                "hierarchyLevel": 0
            },
            {
                "self": "https://fatec/rest/api/3/issuetype/10553",
                "id": "10553",
                "description": "As histórias monitoram funções ou recursos expressos como objetivos do usuário.",
                "iconUrl": "https://fatec/rest/api/2/universal_avatar/view/type/issuetype/avatar/10315?size=medium",
                "name": "História",
                "subtask": False,
                "avatarId": 10315,
                "hierarchyLevel": 0
            },
            {
                "self": "https://fatec/rest/api/3/issuetype/10554",
                "id": "10554",
                "description": "Os epics monitoram coleções de tarefas, histórias e bugs relacionados.",
                "iconUrl": "https://fatec/rest/api/2/universal_avatar/view/type/issuetype/avatar/10307?size=medium",
                "name": "Epic",
                "subtask": False,
                "avatarId": 10307,
                "hierarchyLevel": 1
            },
            {
                "self": "https://fatec/rest/api/3/issuetype/10555",
                "id": "10555",
                "description": "As subtarefas monitoram pequenas partes do trabalho que fazem parte de uma tarefa maior.",
                "iconUrl": "https://fatec/rest/api/2/universal_avatar/view/type/issuetype/avatar/10316?size=medium",
                "name": "Subtarefa",
                "subtask": True,
                "avatarId": 10316,
                "hierarchyLevel": -1
            }
        ],
        "name": "SOS MNT 2025",
        "avatarUrls": {
            "48x48": "https://fatec/rest/api/3/universal_avatar/view/type/project/avatar/10423",
        },
        "projectKeys": [
            "SM2"
        ],
        "projectTypeKey": "software",
        "simplified": True,
        "style": "next-gen",
        "isPrivate": False,
        "properties": {},
        "entityId": "e915ce14-18fc-417a-92fb",
        "uuid": "e915ce14-18fc-417a-92fb"
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
            "active": True
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
                "hierarchyLevel": 0
            },
            {
                "self": "https://fatec/rest/api/3/issuetype/10560",
                "id": "10560",
                "description": "Os epics monitoram coleções de tarefas, histórias e bugs relacionados.",
                "iconUrl": "https://fatec/rest/api/2/universal_avatar/view/type/issuetype/avatar/10307?size=medium",
                "name": "Epic",
                "subtask": False,
                "avatarId": 10307,
                "hierarchyLevel": 1
            },
            {
                "self": "https://fatec/rest/api/3/issuetype/10561",
                "id": "10561",
                "description": "As subtarefas monitoram pequenas partes do trabalho que fazem parte de uma tarefa maior.",
                "iconUrl": "https://fatec/rest/api/2/universal_avatar/view/type/issuetype/avatar/10316?size=medium",
                "name": "Subtarefa",
                "subtask": True,
                "avatarId": 10316,
                "hierarchyLevel": -1
            },
            {
                "self": "https://fatec/rest/api/3/issuetype/10625",
                "id": "10625",
                "description": "Erros rastreiam problemas ou erros.",
                "iconUrl": "https://fatec/rest/api/2/universal_avatar/view/type/issuetype/avatar/10303?size=medium",
                "name": "Erro",
                "subtask": False,
                "avatarId": 10303,
                "hierarchyLevel": 0
            }
        ],
        "name": "SOS Edital",
        "avatarUrls": {
            "48x48": "https://fatec/rest/api/3/universal_avatar/view/type/project/avatar/10412",
        },
        "projectKeys": [
            "SE"
        ],
        "projectTypeKey": "software",
        "simplified": True,
        "style": "next-gen",
        "isPrivate": False,
        "properties": {},
        "entityId": "950c63a2-e6bb-4e5d-8390",
        "uuid": "950c63a2-e6bb-4e5d-8390"
    }
]