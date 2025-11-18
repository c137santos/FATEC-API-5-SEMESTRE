import json
from unittest.mock import ANY, Mock

import pytest
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.test import RequestFactory

from jiboia.base.exceptions import BusinessError
from jiboia.base.middlewares import CsrfTokenExemptionMiddleware, DjavueApiErrorHandlingMiddleware


@pytest.fixture
def authenticated_client(client, db):
    """Creates a client with an authenticated user"""
    User = get_user_model()
    user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass")
    client.force_login(user)
    return client


def test_obter_status(authenticated_client):
    resp = authenticated_client.get("/api/status")
    assert resp.status_code == 200
    assert resp.json() == {
        "status": "ok",
        "db": "ok",
        "git_hash": ANY,
    }


def test_process_exception_value_error():
    """Testa o tratamento de ValueError no middleware"""
    middleware = DjavueApiErrorHandlingMiddleware(lambda r: None)
    request = Mock()
    exception = ValueError("Valor inválido")

    response = middleware.process_exception(request, exception)

    assert isinstance(response, JsonResponse)
    assert response.status_code == 422

    response_data = json.loads(response.content.decode())
    assert "INVALID INPUT" in response_data["message"]
    assert "Valor inválido" in response_data["message"]


def test_process_exception_business_error():
    """Testa o tratamento de BusinessError no middleware"""
    middleware = DjavueApiErrorHandlingMiddleware(lambda r: None)
    request = Mock()
    exception = BusinessError("Erro de negócio")

    response = middleware.process_exception(request, exception)

    assert isinstance(response, JsonResponse)
    assert response.status_code == 400

    response_data = json.loads(response.content.decode())
    assert "ERROR" in response_data["message"]
    assert "Erro de negócio" in response_data["message"]


def test_process_exception_generic_exception():
    """Testa o tratamento de exceções genéricas no middleware"""
    middleware = DjavueApiErrorHandlingMiddleware(lambda r: None)
    request = Mock()
    exception = Exception("Erro qualquer")

    response = middleware.process_exception(request, exception)

    assert isinstance(response, JsonResponse)
    assert response.status_code == 503

    response_data = json.loads(response.content.decode())
    assert "UNAVAILABLE" in response_data["message"]
    assert "Erro qualquer" in response_data["message"]


def test_csrf_middleware_with_authorization():
    """Testa que CSRF é desabilitado quando há header Authorization"""

    factory = RequestFactory()
    request = factory.get("/")
    request.META["HTTP_AUTHORIZATION"] = "Bearer token123"

    middleware = CsrfTokenExemptionMiddleware(lambda r: None)
    response = middleware.process_view(request, None, [], {})

    assert hasattr(request, "_dont_enforce_csrf_checks")
    assert request._dont_enforce_csrf_checks is True
    assert response is None


def test_csrf_middleware_without_authorization():
    """Testa que CSRF não é desabilitado sem header Authorization"""
    factory = RequestFactory()
    request = factory.get("/")
    if "HTTP_AUTHORIZATION" in request.META:
        del request.META["HTTP_AUTHORIZATION"]

    middleware = CsrfTokenExemptionMiddleware(lambda r: None)
    response = middleware.process_view(request, None, [], {})

    assert not hasattr(request, "_dont_enforce_csrf_checks")
    assert response is None
