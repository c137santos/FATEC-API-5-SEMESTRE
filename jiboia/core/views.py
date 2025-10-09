# coding: utf-8
import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from jiboia.core.service import projects_svc

from ..commons.django_views_utils import ajax_login_required
from .service import issues_svc, project_overview_svc

logger = logging.getLogger(__name__)


@require_http_methods(["POST"])
@ajax_login_required
def add_issue(request):
    """Adiciona Issue"""
    logger.info("API add new issue.")
    body = json.loads(request.body)
    description = body.get("description")

    if not description:
        raise ValueError("body.issue.description: Field required (missing)")
    if type(description) not in [str]:
        raise ValueError("body.issue.description: Input should be a valid string (string_type)")

    description = str(description)
    if len(description) <= 2:
        raise ValueError("body.issue.description: Value error, It must be at least 3 characteres long. (value_error)")

    new_issue = issues_svc.add_issue(description)

    return JsonResponse(new_issue, status=201)


@require_http_methods(["GET"])
def list_paginable_issues(request):
    """List Issues in pages"""

    logger.info("API list issues")
    page_number = request.GET.get("page", 1)

    try:
        page_number = int(page_number)

    except (TypeError, ValueError):
        page_number = 1

    issues_data = issues_svc.list_issues(page_number)
    return JsonResponse(issues_data)


@require_http_methods(["GET"])
def project_overview(request, project_id):
    """
    Get detailed overview of a specific project
    """
    logger.info(f"API get project overview for project_id={project_id}")

    issues_breakdown_months = request.GET.get("issues_breakdown_months", 6)
    burndown_days = request.GET.get("burdown_days", 5)

    try:
        issues_breakdown_months = int(issues_breakdown_months)
        burndown_days = int(burndown_days)
    except (ValueError, TypeError):
        return JsonResponse(
            {"error": "Invalid parameters: issues_breakdown_months and burndown_days must be integers"}, status=400
        )

    overview_data = project_overview_svc.get_project_overview(
        project_id, issues_breakdown_months=issues_breakdown_months, burndown_days=burndown_days
    )

    if overview_data is None:
        return JsonResponse({"error": f"Project with ID {project_id} not found"}, status=404)

    return JsonResponse(overview_data)


@require_http_methods(["GET"])
def list_projects_general(request):
    logger.info("API list projects")

    issue_breakdown_months = int(request.GET.get("issues_breakdown_months", 1))
    projects = projects_svc.list_projects_general(issue_breakdown_months)

    return JsonResponse(projects)
