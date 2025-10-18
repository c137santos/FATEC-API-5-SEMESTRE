from asyncio.log import logger

from jiboia.core.models import StatusType


def list_status_type():
    logger.info("SERVICE list status types")
    status_types = StatusType.objects.all()
    serializers = []
    for i in status_types:
        serializer = {
            "statustype_id": i.id,
            "name": i.name,
            "jira_id": i.jira_id,
        }
        serializers.append(serializer)
    return serializers
