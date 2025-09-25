from jiboia.core.models import Project


def save_projects(projects_data):
    """
    Save or update a list of projects in the database.

    Args:
        projects_data (list[dict]): List of project dictionaries with Jira data.
    """
    for proj in projects_data:
        Project.objects.update_or_create(
            jira_id=proj["jira_id"],
            defaults={
                "key": proj.get("key"),
                "name": proj.get("name"),
                "description": proj.get("description", ""),
                "start_date": proj.get("start_date_project"),
                "end_date": proj.get("end_date_project"),
                "uuid": proj.get("uuid"),
                "jira_id": proj.get("jira_id"),
                "projectTypeKey": proj.get("projectTypeKey"),
            }
        )