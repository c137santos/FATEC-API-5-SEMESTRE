import logging

import requests
from django.contrib.auth import get_user_model

from jiboia.core.models import Issue, IssueType, Project, TimeLog
from jiboia.core.service.strategy.users import SyncUserStrategy

from .base import JiraStrategy

logger = logging.getLogger(__name__)
User = get_user_model()


class SyncIssuesStrategy(JiraStrategy[int]):
    """
    Synchronizes issues from a Jira project, including worklogs and changelog.
    """
    def _get_worklog_comment_text(self, comment):
        if not comment:
            return ""
        content = comment.get("content", [])
        if not content:
            return ""
        inner = content[0].get("content", []) if isinstance(content[0], dict) else []
        if not inner:
            return ""
        return inner[0].get("text", "") if isinstance(inner[0], dict) else ""
    _ENDPOINT = "/rest/api/3/search/jql"
    _MAX_RESULTS = 100

    def execute(self, project_key: str) -> int:
        logger.info(f"Starting synchronization of issues for project '{project_key}'...")
        synced_count = 0
        start_at = 0
        try:
            project = Project.objects.get(key=project_key)
        except Project.DoesNotExist:
            logger.error(
                f"Project with key '{project_key}' not found in the database. "
                "Sync projects first."
            )
            return 0
        while True:
            logger.info(f"Fetching issues starting at index {start_at}...")
            params = {
                "jql": f"project = {project_key} ORDER BY updated DESC",
                "expand": "changelog",
                "fields": "*all",
                "startAt": start_at,
                "maxResults": self._MAX_RESULTS,
            }
            response = requests.get(
                f"{self.base_url}{self._ENDPOINT}",
                params=params,
                auth=(self.email, self.token),
                timeout=30
            )
            data = response.json()
            issues_data = data.get("issues", [])
            if not issues_data:
                break
            for issue_data in issues_data:
                issue_obj = self._sync_issue(issue_data, project)
                self._sync_worklogs(issue_obj, issue_data)
                synced_count += 1
            if (start_at + len(issues_data)) >= data.get("total", 0):
                break
            start_at += len(issues_data)
        logger.info(f"Issues synchronization for project '{project_key}' finished. Total: {synced_count}.")
        return synced_count

    def _sync_issue(self, data: dict, project: Project) -> Issue:
        fields = data.get("fields", {})
        
        assignee = None
        if assignee_data := fields.get("assignee"):
            assignee = SyncUserStrategy().execute(assignee_data)

        issue_type = None
        if type_data := fields.get("issuetype"):
            issue_type = IssueType.objects.get(jira_id=type_data['id'])
        
        start_date = fields.get("customfield_10015")
        time_estimate_seconds = fields.get("timeestimate")
        issue_obj, created = Issue.objects.update_or_create(
            jira_id=data['id'],
            defaults={
                "project": project,
                "type_issue": issue_type,
                "id_user": assignee,
                "description": fields.get("summary", ""),
                    "details": (
                        fields.get("description", {})
                        .get('content', [{}])[0]
                        .get('content', [{}])[0]
                        .get('text', '')
                        if fields.get("description")
                        else ""
                    ),
                "created_at": fields.get("created"),
                "end_date": fields.get("resolutiondate"),
                "time_estimate_seconds": time_estimate_seconds,
                "start_date": start_date,
            }
        )
        return issue_obj

    def _sync_worklogs(self, issue_obj: Issue, data: dict):
        worklogs = data.get("fields", {}).get("worklog", {}).get("worklogs", [])
        for log_data in worklogs:
            author = None
            if author_data := log_data.get("author"):
                author = SyncUserStrategy().execute(author_data)
            TimeLog.objects.update_or_create(
                jira_id=log_data['id'],
                defaults={
                    "id_issue": issue_obj,
                    "id_user": author,
                    "seconds": log_data.get("timeSpentSeconds", 0),
                    "log_date": log_data.get("started"),
                    "description_log": self._get_worklog_comment_text(log_data.get("comment"))
                }
            )
