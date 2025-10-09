from unittest.mock import MagicMock

import pytest

from jiboia.core.service.strategy.users import SyncUserStrategy


@pytest.fixture
def mock_user_model(monkeypatch):
    class DummyUser:
        objects = MagicMock()

    monkeypatch.setattr("django.contrib.auth.get_user_model", lambda: DummyUser)
    return DummyUser


def test_execute_user(monkeypatch, mock_user_model):
    strategy = SyncUserStrategy()
    user_data = {"accountId": "abc", "displayName": "Test User"}
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "accountId": "abc",
        "displayName": "Test User",
        "emailAddress": "test@example.com",
    }
    mock_response.raise_for_status = MagicMock()
    monkeypatch.setattr("requests.get", lambda *a, **k: mock_response)
    import jiboia.core.service.strategy.users as users_mod

    users_mod.User = MagicMock()
    users_mod.User.objects.get_or_create.return_value = (MagicMock(), True)
    result = strategy.execute(user_data, email="e", token="t", base_url="http://fake-jira")
    assert result is not None


def test_execute_user_missing_accountid(monkeypatch, mock_user_model):
    strategy = SyncUserStrategy()
    user_data = {"displayName": "Test User"}
    result = strategy.execute(user_data, email="e", token="t", base_url="http://fake-jira")
    assert result is None


def test_execute_user_missing_email(monkeypatch, mock_user_model):
    strategy = SyncUserStrategy()
    user_data = {"accountId": "abc", "displayName": "Test User"}
    result = strategy.execute(user_data, email=None, token="t", base_url="http://fake-jira")
    assert result is None


def test_execute_user_request_exception(monkeypatch, mock_user_model):
    strategy = SyncUserStrategy()
    user_data = {"accountId": "abc", "displayName": "Test User"}

    def raise_exc(*a, **k):
        raise Exception("request error")

    monkeypatch.setattr("requests.get", raise_exc)
    result = strategy.execute(user_data, email="e", token="t", base_url="http://fake-jira")
    assert result is None or result


def test_execute_user_missing_fields_in_response(monkeypatch, mock_user_model):
    strategy = SyncUserStrategy()
    user_data = {"accountId": "abc", "displayName": "Test User"}
    mock_response = MagicMock()
    mock_response.json.return_value = {"accountId": "abc", "displayName": "Test User"}
    mock_response.raise_for_status = MagicMock()
    monkeypatch.setattr("requests.get", lambda *a, **k: mock_response)
    result = strategy.execute(user_data, email="e", token="t", base_url="http://fake-jira")
    assert result is not None
