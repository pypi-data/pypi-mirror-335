import pytest
import requests_mock
from weni.clients.dl_manager_client import DLManagerClient
from weni.paths import MsgPath
from weni.utils.exceptions import ValidationError, DLManagerError


BASE_URL = "https://dl-manager.example.com/api"

@pytest.fixture
def client():
    return DLManagerClient(base_url=BASE_URL)

def test_insert_data_success(client):
    with requests_mock.Mocker() as m:
        m.post(f"{BASE_URL}/messages/send", json={"status": "success"}, status_code=200)

        msg_instance = dict(project_uuid="68c84e84-2d7d-4dc7-8193-50d0e2321b2e", text="Oi!")
        response = client.insert(MsgPath, msg_instance)
        assert response == {"status": "success"}

def test_insert_data_fail_dl_manager(client):
    with requests_mock.Mocker() as m:
        m.post(f"{BASE_URL}/messages/send", status_code=500, json={"error": "Internal Server Error"})

        with pytest.raises(DLManagerError):
            client.insert(MsgPath, dict(project_uuid="68c84e84-2d7d-4dc7-8193-50d0e2321b2e", text="Oi!"))
