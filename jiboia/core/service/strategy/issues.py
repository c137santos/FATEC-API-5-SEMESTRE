import logging

import requests
from django.contrib.auth import get_user_model
from django.db.models import Max, Min

from jiboia.core.models import Issue, IssueType, Project, StatusType, TimeLog
from jiboia.core.service.strategy.users import SyncUserStrategy

from .base import JiraStrategy

logger = logging.getLogger(__name__)
User = get_user_model()


class SyncIssuesStrategy(JiraStrategy[int]):

    @staticmethod
    def update_project_dates(project: Project):
        """
        Updates the project's start_date_project to the earliest start_date
        and end_date_project to the latest end_date among its issues.
        """
        issues = project.issue_set.all()
        min_start = issues.aggregate(Min('start_date'))['start_date__min']
        max_end = issues.aggregate(Max('end_date'))['end_date__max']
        if min_start:
            project.start_date_project = min_start.date() if hasattr(min_start, 'date') else min_start
        if max_end:
            project.end_date_project = max_end.date() if hasattr(max_end, 'date') else max_end
        project.save()

    def _get_worklog_comment_text(self, comment):
        content = []
        if comment:
            content = comment if isinstance(comment, list) else comment.get("content", [])
        if content:
            inner = content[0].get("content", []) if isinstance(content[0], dict) else []
            if inner:
                return inner[0].get("text", "") if isinstance(inner[0], dict) else ""
        return ""

    _ENDPOINT = "/rest/api/3/search/jql"
    _MAX_RESULTS = 100
    
    def execute(self, project_key: str) -> int:
        logger.info(f"Starting synchronization of issues for project '{project_key}'...")
        synced_count = 0
        try:
            project = Project.objects.get(key=project_key)
        except Project.DoesNotExist:
            logger.error(
                f"Project with key '{project_key}' not found in the database. "
                "Sync projects first."
            )
            return 0
        
        start_at = 0
        max_results = 100
        total_issues = None
        page_count = 0
        
        while start_at >= 0:  # Condição mais clara que while True
            params = {
                "jql": f"project = {project_key} ORDER BY updated DESC",
                "expand": "changelog",
                "fields": "*all",
                "maxResults": max_results,
                "startAt": start_at,
            }
            
            response = requests.get(
                f"{self.base_url}{self._ENDPOINT}",
                params=params,
                auth=(self.email, self.token),
                timeout=30
            )
            data = response.json()
            
            if total_issues is None:
                total_issues = data.get("total", 0)
                logger.info(f"Found {total_issues} total issues for project '{project_key}'")
            
            issues_data = data.get("issues", [])
            
            if not issues_data:
                break
                
            page_count += 1
            logger.info(f"Processing page {page_count} - {len(issues_data)} issues")
                
            for issue_data in issues_data:
                issue_obj = self._sync_issue(issue_data, project)
                self._sync_worklogs(issue_obj, issue_data)
                synced_count += 1
            
            start_at += max_results
            
            # Se pegamos menos issues que o maxResults, chegamos ao fim
            if len(issues_data) < max_results:
                break
        
        self.update_project_dates(project)
        logger.info(
            f"Issues synchronization for project '{project_key}' finished. Total: {synced_count}/{total_issues}."
        )
        return synced_count

    def _sync_issue(self, data: dict, project: Project) -> Issue:
        fields = data.get("fields", {})
        
        assignee = None
        if assignee_data := fields.get("assignee"):
            assignee = SyncUserStrategy().execute(assignee_data, self.email, self.token, self.base_url)

        issue_type = None
        if type_data := fields.get("issuetype"):
            issue_type = IssueType.objects.get(jira_id=type_data['id'])
        
        status = None
        if status_data := fields.get("status"):
            try:
                status = StatusType.objects.get(jira_id=status_data['id'])
            except StatusType.DoesNotExist:
                logger.warning(f"Status with jira_id {status_data['id']} not found. Sync status types first.")
        
        start_date = fields.get("customfield_10015")
        time_estimate_seconds = fields.get("timeestimate")
        issue_obj, created = Issue.objects.update_or_create(
            jira_id=data['id'],
            defaults={
                "project": project,
                "type_issue": issue_type,
                "status": status,
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
                author = SyncUserStrategy().execute(author_data, self.email, self.token, self.base_url)
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