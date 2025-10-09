import logging

import requests
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class SyncUserStrategy:
    """
    Synchronizes or updates a Jira user in the local database.
    Receives a dictionary of Jira user data (assignee, author, etc).
    """

    def execute(self, user_data: dict, email=None, token=None, base_url=None) -> User:
        if not user_data or not user_data.get("accountId") or not email or not token or not base_url:
            return None
        url = f"{base_url}/rest/api/3/user"
        params = {"accountId": user_data["accountId"]}
        try:
            resp = requests.get(url, params=params, auth=(email, token), timeout=15)
            resp.raise_for_status()
            user_data = resp.json()
        except Exception as e:
            logger.error(f"Error fetching user {user_data['accountId']} from Jira: {e}")
        email_val = user_data.get("emailAddress") or user_data.get("email")
        username = user_data.get("displayName") or user_data.get("name") or user_data.get("accountId")
        display = user_data.get("displayName") or user_data.get("name") or ""
        first_name = user_data.get("firstName") or ""
        last_name = user_data.get("lastName") or ""
        if not username:
            username = f"jira_{display.replace(' ', '_')}"
        defaults = {
            "email": email_val or "",
            "first_name": first_name,
            "last_name": last_name,
        }
        user, _ = User.objects.get_or_create(username=username, defaults=defaults)
        changed = False
        for k, v in defaults.items():
            if getattr(user, k, None) != v:
                setattr(user, k, v)
                changed = True
        if changed:
            user.save()
        return user
