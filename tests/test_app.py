from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_root(mocker):
    dynamodb_mock = mocker.MagicMock(name="bucket_mock")
    mocker.patch("api.main.boto3.resource", return_value=dynamodb_mock)
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {'message': 'application is running', 'status': 200}
