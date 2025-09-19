from unittest.mock import patch

from freezegun import freeze_time

from jiboia.core.cron import jira_healthcheck


class TestCronJobs:

    @freeze_time("2025-09-19 00:00:01")
    @patch('jiboia.core.cron.JiraService.healthcheck')
    def test_jira_healthcheck_success(self, mock_healthcheck):
        mock_healthcheck.return_value = (True, "OK - 5 projects found")

        result = jira_healthcheck()

        assert result is True
        mock_healthcheck.assert_called_once()

    @freeze_time("2025-09-19 00:00:01")
    @patch('jiboia.core.cron.JiraService.healthcheck')
    def test_jira_healthcheck_failure(self, mock_healthcheck):
        mock_healthcheck.return_value = (False, "Failed with status 500")

        result = jira_healthcheck()

        assert result is False
        mock_healthcheck.assert_called_once()

    @freeze_time("2025-09-19 00:00:01")
    @patch('jiboia.core.cron.JiraService.healthcheck')
    @patch('jiboia.core.cron.logger')
    def test_jira_healthcheck_logging_success(self, mock_logger, mock_healthcheck):
        mock_healthcheck.return_value = (True, "OK - 5 projects found")

        jira_healthcheck()

        assert mock_logger.info.call_count == 2
        mock_logger.error.assert_not_called()
        
        mock_logger.info.assert_any_call(
            '[CRON] Starting Jira API healthcheck at 2025-09-19 00:00:01'
        )
        
        mock_logger.info.assert_any_call(
            '[CRON] Jira API healthcheck completed successfully in 0.00s: OK - 5 projects found'
        )

    @freeze_time("2025-09-19 00:00:01")
    @patch('jiboia.core.cron.JiraService.healthcheck')
    @patch('jiboia.core.cron.logger')
    def test_jira_healthcheck_logging_failure(self, mock_logger, mock_healthcheck):
        mock_healthcheck.return_value = (False, "Failed with status 500")

        jira_healthcheck()

        assert mock_logger.info.call_count == 1
        assert mock_logger.error.call_count == 1
        
        mock_logger.info.assert_called_once_with(
            '[CRON] Starting Jira API healthcheck at 2025-09-19 00:00:01'
        )
        
        mock_logger.error.assert_called_once_with(
            '[CRON] Jira API healthcheck failed after 0.00s: Failed with status 500'
        )