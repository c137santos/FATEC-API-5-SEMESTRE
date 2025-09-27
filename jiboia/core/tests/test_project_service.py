import pytest
from jiboia.core.models import Project
from jiboia.core.service.projects_svc import save_projects

@pytest.mark.django_db
def test_save_projects_creates_new_projects():
    projects_data = [
        {
            "jira_id": 1,
            "key": "PROJ1",
            "name": "Projeto 1",
            "description": "Desc 1",
            "start_date_project": "2024-01-01",
            "end_date_project": "2024-12-31",
            "uuid": "uiahisuah",
            "projectTypeKey": "software"
        },
        {
            "jira_id": 2,
            "key": "PROJ2",
            "name": "Projeto 2",
            "description": "Desc 2",
            "start_date_project": "2024-02-01",
            "end_date_project": "2024-11-30",
            "uuid": "aloualoui",
            "projectTypeKey": "business"
        }
    ]

    save_projects(projects_data)

    assert Project.objects.count() == 2
    proj1 = Project.objects.get(jira_id=1)
    assert proj1.name == "Projeto 1"
    assert proj1.description == "Desc 1"
    assert str(proj1.start_date_project) == "2024-01-01"
    assert str(proj1.end_date_project) == "2024-12-31"
    assert proj1.uuid == "uiahisuah"
    assert proj1.projectTypeKey == "software"

    proj2 = Project.objects.get(jira_id=2)
    assert proj2.name == "Projeto 2"
    assert proj2.description == "Desc 2"
    assert str(proj2.start_date_project) == "2024-02-01"
    assert str(proj2.end_date_project) == "2024-11-30"
    assert proj2.uuid == "aloualoui"
    assert proj2.projectTypeKey == "business"

@pytest.mark.django_db
def test_save_projects_updates_existing_project():
    Project.objects.create(
        jira_id=1,
        key="PROJ1",
        name="Projeto Antigo",
        description="Desc Antiga",
        start_date_project="2024-01-01",
        end_date_project="2024-12-31",
        uuid=101,
        projectTypeKey="software"
    )

    projects_data = [
        {
            "jira_id": 1,
            "key": "PROJ1",
            "name": "Projeto Atualizado",
            "description": "Nova descrição",
            "start_date_project": "2024-01-01",
            "end_date_project": "2024-12-31",
            "uuid": "101",
            "projectTypeKey": "software"
        }
    ]

    save_projects(projects_data)

    proj = Project.objects.get(jira_id=1)
    assert proj.name == "Projeto Atualizado"
    assert proj.description