"""
Testes para as funções de cron jobs.
"""
import pytest
from unittest.mock import patch, MagicMock
from freezegun import freeze_time
from datetime import datetime

from jiboia.core.cron import jira_healthcheck


class TestCronJobs:
    """Testes para as funções de cron jobs."""

    @freeze_time("2025-09-19 00:00:01")
    @patch('jiboia.core.cron.JiraService.healthcheck')
    def test_jira_healthcheck_success(self, mock_healthcheck):
        """
        Testa o caso de sucesso da função de cron jira_healthcheck.
        """
        # Configurar o mock para simular um healthcheck bem-sucedido
        mock_healthcheck.return_value = (True, "OK - 5 projetos encontrados")

        # Executar a função de cron
        result = jira_healthcheck()

        # Verificar o resultado
        assert result is True
        mock_healthcheck.assert_called_once()

    @freeze_time("2025-09-19 00:00:01")
    @patch('jiboia.core.cron.JiraService.healthcheck')
    def test_jira_healthcheck_failure(self, mock_healthcheck):
        """
        Testa o caso de falha da função de cron jira_healthcheck.
        """
        # Configurar o mock para simular um healthcheck com falha
        mock_healthcheck.return_value = (False, "Falhou com status 500")

        # Executar a função de cron
        result = jira_healthcheck()

        # Verificar o resultado
        assert result is False
        mock_healthcheck.assert_called_once()

    @freeze_time("2025-09-19 00:00:01")
    @patch('jiboia.core.cron.JiraService.healthcheck')
    @patch('jiboia.core.cron.logger')
    def test_jira_healthcheck_logging_success(self, mock_logger, mock_healthcheck):
        """
        Testa se os logs são registrados corretamente em caso de sucesso.
        """
        # Configurar o mock para simular um healthcheck bem-sucedido
        mock_healthcheck.return_value = (True, "OK - 5 projetos encontrados")

        # Executar a função de cron
        jira_healthcheck()

        # Verificar se os logs foram registrados corretamente
        assert mock_logger.info.call_count == 2
        mock_logger.error.assert_not_called()
        
        # Verificar a primeira chamada (início do healthcheck)
        mock_logger.info.assert_any_call(
            '[CRON] Iniciando healthcheck da API do Jira em 2025-09-19 00:00:01'
        )
        
        # Verificar a segunda chamada (fim do healthcheck)
        # Como estamos usando freeze_time, duration será 0
        mock_logger.info.assert_any_call(
            '[CRON] Healthcheck da API do Jira concluído com sucesso em 0.00s: OK - 5 projetos encontrados'
        )

    @freeze_time("2025-09-19 00:00:01")
    @patch('jiboia.core.cron.JiraService.healthcheck')
    @patch('jiboia.core.cron.logger')
    def test_jira_healthcheck_logging_failure(self, mock_logger, mock_healthcheck):
        """
        Testa se os logs são registrados corretamente em caso de falha.
        """
        # Configurar o mock para simular um healthcheck com falha
        mock_healthcheck.return_value = (False, "Falhou com status 500")

        # Executar a função de cron
        jira_healthcheck()

        # Verificar se os logs foram registrados corretamente
        assert mock_logger.info.call_count == 1
        assert mock_logger.error.call_count == 1
        
        # Verificar a primeira chamada (início do healthcheck)
        mock_logger.info.assert_called_once_with(
            '[CRON] Iniciando healthcheck da API do Jira em 2025-09-19 00:00:01'
        )
        
        # Verificar a chamada de erro
        # Como estamos usando freeze_time, duration será 0
        mock_logger.error.assert_called_once_with(
            '[CRON] Healthcheck da API do Jira falhou após 0.00s: Falhou com status 500'
        )