# coding: utf-8
import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ..commons.django_views_utils import ajax_login_required
from .service import issues_svc, project_svc

logger = logging.getLogger(__name__)


@require_http_methods(["POST"])
@csrf_exempt
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
        raise ValueError(
            "body.issue.description: Value error, It must be at least 3 characteres long. (value_error)"
        )

    new_issue = issues_svc.add_issue(description)

    return JsonResponse(new_issue, status=201)



@require_http_methods(["GET"])
@ajax_login_required

def list_issues(request):
    """Lista Issues"""
    logger.info("API list issues")
    issues = issues_svc.list_issues()
    return JsonResponse({"issues": issues})


@require_http_methods(["GET"])

def list_projects_general(request):
    logger.info("API list projects")
    
    issue_breakdown_months = int(request.GET.get("issues_breakdown_months", 1))
    projects = project_svc.list_projects_general(issue_breakdown_months)
    
    return JsonResponse(projects)
