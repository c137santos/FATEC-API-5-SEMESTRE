from jiboia.core.models import StatusType


def list_status_type():
    status_types = StatusType.objects.all()
    serializers = []
    for i in status_types:
        serializer = {"statustype_id": i.id, "name": i.name, "jira_id": i.jira_id, "key": i.key}
        serializers.append(serializer)
    return serializers
