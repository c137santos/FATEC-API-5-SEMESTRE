# coding: utf-8
import json
import logging
import threading

from django.http import JsonResponse
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from jiboia.core.cron import jira_full_sync
from jiboia.core.service import projects_svc

from ..commons.django_views_utils import ajax_login_required
from .service import issues_svc, project_overview_svc

logger = logging.getLogger(__name__)

jira_sync_lock = threading.Lock()


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


@cache_control()
@require_http_methods(["GET"])
@ajax_login_required
def list_paginable_issues(request, project_id):
    """List Issues in pages"""
    logger.info(f"API list issues for project {project_id}")

    page_number = request.GET.get("page", 1)
    items_per_page = request.GET.get("itemsPerPage", 10)

    try:
        page_number = int(page_number)
        items_per_page = int(items_per_page)

    except (TypeError, ValueError):
        page_number = 1
        items_per_page = 10

    issues_data = issues_svc.list_issues(project_id, page_number, items_per_page)
    return JsonResponse(issues_data)


@cache_control()
@require_http_methods(["GET"])
@ajax_login_required
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


@cache_control()
@require_http_methods(["GET"])
@ajax_login_required
def list_projects_general(request):
    logger.info("API list projects")

    issue_breakdown_months = int(request.GET.get("issues_breakdown_months", 1))
    projects = projects_svc.list_projects_general(issue_breakdown_months)

    return JsonResponse(projects)


@require_http_methods(["GET"])
@ajax_login_required
def project_developers(request, project_id):
    developers = projects_svc.get_project_developers(project_id)

    return JsonResponse(developers, safe=False)


@csrf_exempt
@require_http_methods(["PATCH"])
@ajax_login_required
def update_developer_hour_value(request, project_id, user_id):
    """
    Update the hourly rate (valor_hora) for a specific developer in a project.
    """
    logger.info(f"API update developer hour value for project_id={project_id}, user_id={user_id}")

    try:
        body = json.loads(request.body)
        valor_hora = body.get("valorHora")
        hour_updated = projects_svc.update_developer_hour_value(project_id, user_id, valor_hora)

        return JsonResponse(hour_updated, status=200)

    except ValueError as e:
        logger.error(f"ValueError updating developer hour value: {e}")
        return JsonResponse({"error": str(e)}, status=400)

    except Exception as e:
        logger.error(f"Error updating developer hour value: {e}")
        return JsonResponse({"error": "Internal server error"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@ajax_login_required
def trigger_jira_sync(request):
    if not jira_sync_lock.acquire(blocking=False):
        logger.warning("Uma sincronização já está em andamento. Nova requisição bloqueada.")
        return JsonResponse({"status": "error", "message": "Uma sincronização já está em andamento."}, status=409)
    try:

        def sync_and_release_lock():
            try:
                logger.info("Iniciando jira_full_sync na thread...")
                jira_full_sync()
            except Exception as e:
                logger.error(f"Erro na thread de sincronização: {e}", exc_info=True)
            finally:
                logger.info("Sincronização terminada. Soltando o cadeado.")
                jira_sync_lock.release()

        sync_thread = threading.Thread(target=sync_and_release_lock)
        sync_thread.start()

        logger.info("Atualizando dados do Jira, aguarde...")
        return JsonResponse(
            {"status": "success", "message": "A sincronização foi iniciada em segundo plano."}, status=202
        )

    except Exception as e:
        logger.error(f"Falha ao iniciar a thread de sincronização: {e}")
        jira_sync_lock.release()
        return JsonResponse(
            {"status": "error", "message": f"Falha ao iniciar a tarefa de sincronização: {str(e)}"}, status=500
        )
