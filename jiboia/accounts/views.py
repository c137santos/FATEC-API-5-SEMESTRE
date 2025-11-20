# coding: utf-8

import json
import logging

from django.contrib import auth
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from jiboia.accounts.models import User
from jiboia.accounts.services import create_user as create_user_service
from jiboia.accounts.services import delete_user as delete_user_service

logger = logging.getLogger(__name__)


@csrf_exempt
def login(request):
    """
    Login do usuário e criação de uma nova sessão
    """
    logger.info("API login")
    body = json.loads(request.body)
    username = body["username"]
    password = body["password"]
    user_authenticaded = auth.authenticate(username=username, password=password)
    user_dict = None
    if user_authenticaded is not None and user_authenticaded.is_active:
        auth.login(request, user_authenticaded)
        user_dict = user_authenticaded.to_dict_json()
        logger.info("API login success")
    if not user_dict:
        user_dict = {"message": "Unauthorized"}
        return JsonResponse(user_dict, safe=False, status=401)
    return JsonResponse(user_dict, safe=False, status=201)


def logout(request):
    """
    Encerra sessão do usuário
    """
    if request.method.lower() != "post":
        raise ValueError("Logout only via post")
    logger.info(f"API logout: {request.user.username}")
    auth.logout(request)
    return JsonResponse({})


def whoami(request):
    """
    Retorna dados do usuário logado
    """
    user_data = {"authenticated": False}
    if request.user.is_authenticated:
        user_data["authenticated"] = True
        user_data["user"] = request.user.to_dict_json()

    logger.info("API whoami")
    return JsonResponse(user_data)


def create_user(request):
    try:
        json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    logger.info("API create_user")
    body = json.loads(request.body)
    name = body["username"]
    password = body["password"]
    email = body["email"]
    permissions = body.get("permissions", {})

    if not any(permissions.values()):
        return JsonResponse(
            {"error": "Pelo menos uma permissão deve ser True"},
            status=400,
        )

    try:
        create_user_service(name, password, email, permissions)
        logger.info("API create_user success")
        return JsonResponse("Usuário criado com sucesso", safe=False, status=201)
    except ValueError as e:
        logger.error(f"API create_user error: {str(e)}")
        return JsonResponse({"message": str(e)}, safe=False, status=400)


def get_all_users(request):
    page = request.GET.get("page", 1)
    try:
        page_size = int(request.GET.get("page_size", 10))
        page_size = min(max(page_size, 1), 100)
    except ValueError:
        page_size = 10

    users = User.objects.all().order_by("id")

    if not users.exists():
        return JsonResponse({"message": "Nenhum usuário encontrado."}, status=404)

    paginator = Paginator(users, page_size)

    try:
        users_page = paginator.page(page)
    except PageNotAnInteger:
        users_page = paginator.page(1)
    except EmptyPage:
        users_page = paginator.page(paginator.num_pages)

    data = {
        "count": paginator.count,
        "total_pages": paginator.num_pages,
        "current_page": users_page.number,
        "results": [user.to_get_user_json() for user in users_page],
    }

    return JsonResponse(data, safe=False, status=200)


# This view intentionally allows both GET (safe) and POST (unsafe) methods
# to handle user listing and creation in one endpoint.
# CSRF protection is disabled because this is a JSON API authenticated by token.


@csrf_exempt
@require_http_methods(["GET", "POST"])
def users_view(request):
    if request.method == "GET":
        return get_all_users(request)
    elif request.method == "POST":
        return create_user(request)


@require_http_methods(["DELETE"])
def delete_user(request, user_id):
    logger.info(f"API delete_user: {user_id}")

    deleted = delete_user_service(user_id)

    if deleted:
        logger.info("API delete_user success")
        return JsonResponse({"message": "Usuário deletado com sucesso"}, status=200)

    logger.warning("API delete_user user not found")
    return JsonResponse({"message": "Usuário não encontrado"}, status=404)
