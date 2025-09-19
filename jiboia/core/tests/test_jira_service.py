"""
Testes para o serviço JiraService que interage com a API do Jira.
"""
import pytest
from unittest.mock import patch, MagicMock
from requests.exceptions import RequestException, ConnectionError, Timeout

from jiboia.core.service.jira_svc import JiraService


class TestJiraService:
    """Testes para o serviço JiraService."""

    @patch('jiboia.core.service.jira_svc.requests.get')
    def test_healthcheck_success(self, mock_get):
        """
        Testa o caso de sucesso do healthcheck da API do Jira.
        """
        # Configurar o mock para simular uma resposta bem-sucedida
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "10000", "key": "PROJ1", "name": "Projeto 1"},
            {"id": "10001", "key": "PROJ2", "name": "Projeto 2"}
        ]
        mock_get.return_value = mock_response

        # Executar o healthcheck
        success, message = JiraService.healthcheck()

        # Verificar o resultado
        assert success is True
        assert "OK - 2 projetos encontrados" in message
        mock_get.assert_called_once()

    @patch('jiboia.core.service.jira_svc.requests.get')
    def test_healthcheck_empty_response(self, mock_get):
        """
        Testa o caso de sucesso com lista vazia de projetos.
        """
        # Configurar o mock para simular uma resposta vazia
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        # Executar o healthcheck
        success, message = JiraService.healthcheck()

        # Verificar o resultado
        assert success is True
        assert "OK - 0 projetos encontrados" in message
        mock_get.assert_called_once()

    @patch('jiboia.core.service.jira_svc.requests.get')
    def test_healthcheck_http_error(self, mock_get):
        """
        Testa o caso de erro HTTP no healthcheck da API do Jira.
        """
        # Configurar o mock para simular uma resposta de erro
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response

        # Executar o healthcheck
        success, message = JiraService.healthcheck()

        # Verificar o resultado
        assert success is False
        assert "Falhou com status 401" in message
        mock_get.assert_called_once()

    @patch('jiboia.core.service.jira_svc.requests.get')
    def test_healthcheck_server_error(self, mock_get):
        """
        Testa o caso de erro de servidor no healthcheck da API do Jira.
        """
        # Configurar o mock para simular uma resposta de erro de servidor
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        # Executar o healthcheck
        success, message = JiraService.healthcheck()

        # Verificar o resultado
        assert success is False
        assert "Falhou com status 500" in message
        mock_get.assert_called_once()

    @patch('jiboia.core.service.jira_svc.requests.get')
    def test_healthcheck_connection_error(self, mock_get):
        """
        Testa o caso de erro de conexão no healthcheck da API do Jira.
        """
        # Configurar o mock para simular um erro de conexão
        mock_get.side_effect = ConnectionError("Falha na conexão")

        # Executar o healthcheck
        success, message = JiraService.healthcheck()

        # Verificar o resultado
        assert success is False
        assert "Falha na conexão" in message
        mock_get.assert_called_once()

    @patch('jiboia.core.service.jira_svc.requests.get')
    def test_healthcheck_timeout(self, mock_get):
        """
        Testa o caso de timeout no healthcheck da API do Jira.
        """
        # Configurar o mock para simular um timeout
        mock_get.side_effect = Timeout("Timeout na requisição")

        # Executar o healthcheck
        success, message = JiraService.healthcheck()

        # Verificar o resultado
        assert success is False
        assert "Timeout na requisição" in message
        mock_get.assert_called_once()

    @patch('jiboia.core.service.jira_svc.requests.get')
    def test_healthcheck_generic_exception(self, mock_get):
        """
        Testa o caso de exceção genérica no healthcheck da API do Jira.
        """
        # Configurar o mock para simular uma exceção genérica
        mock_get.side_effect = Exception("Erro inesperado")

        # Executar o healthcheck
        success, message = JiraService.healthcheck()

        # Verificar o resultado
        assert success is False
        assert "Erro inesperado" in message
        mock_get.assert_called_once()