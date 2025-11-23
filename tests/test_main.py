import pytest
from fastapi.testclient import TestClient
from database import init_db

from main import app


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """테스트 세션 시작 시 데이터베이스 초기화"""
    init_db()
    yield


client = TestClient(app)


def test_add_dream():
    response = client.post(
        "/add_dream/",
        json={"dream_text": "테스트 꿈", "dream_feeling": "행복했다", "user_id": 1},
    )
    if response.status_code != 200:
        print(f"Error response: {response.text}")
    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_search_dreams():
    response = client.get("/search_dreams/?query=친구")
    if response.status_code != 200:
        print(f"Error response: {response.text}")
    assert response.status_code == 200
    assert "results" in response.json()
