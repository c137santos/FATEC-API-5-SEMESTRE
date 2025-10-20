from jiboia.core.models import IssueType


def list_type_issues():
    issues_type_list = IssueType.objects.all()
    serializers = []
    for i in issues_type_list:
        serializer = {
            "issuetype_id": i.id,
            "name": i.name,
            "description": i.description,
            "subtask": i.subtask,
            "jira_id": i.jira_id,
        }
        serializers.append(serializer)
    return serializers
