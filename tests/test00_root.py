from http import client
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# test the root route
def test_root():
    response = client.get("/")
    assert response.json() == [{"Welcome to Personal Finance API": "Our app is under development at https://github.com/fabiodearaujo"}, 200]
