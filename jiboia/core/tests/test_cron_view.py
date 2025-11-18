from unittest.mock import ANY, MagicMock, patch

from django.urls import reverse


@patch("jiboia.core.views.threading.Thread")
@patch("jiboia.core.views.jira_sync_lock")
def test_sync_inicia_com_sucesso_se_lock_livre(mock_lock, mock_thread_class, authenticated_client):
    mock_lock.acquire.return_value = True
    mock_thread_instance = MagicMock()
    mock_thread_class.return_value = mock_thread_instance

    url = reverse("trigger_jira_sync")
    response = authenticated_client.post(url)

    assert response.status_code == 202
    assert response.json() == {"status": "success", "message": "A sincronização foi iniciada em segundo plano."}

    mock_lock.acquire.assert_called_once_with(blocking=False)

    mock_thread_class.assert_called_once_with(target=ANY)
    mock_thread_instance.start.assert_called_once()


@patch("jiboia.core.views.jira_sync_lock")
def test_sync_falha_se_lock_ocupado(mock_lock, authenticated_client):
    mock_lock.acquire.return_value = False

    url = reverse("trigger_jira_sync")
    response = authenticated_client.post(url)

    assert response.status_code == 409
    assert response.json() == {"status": "error", "message": "Uma sincronização já está em andamento."}

    mock_lock.acquire.assert_called_once_with(blocking=False)
    mock_lock.release.assert_not_called()
