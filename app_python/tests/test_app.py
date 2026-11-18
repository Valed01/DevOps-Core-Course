from fastapi.testclient import TestClient

from app import app

client = TestClient(app)

def test_main():
    response = client.get("/")
    
    data = response.json()
    
    assert response.status_code == 200
    assert {
        "service", 
        "system", 
        "runtime", 
        "request", 
        "endpoints"
    }.issubset(data)

def test_health():
    response = client.get("/health")
    
    data = response.json()
    
    assert response.status_code == 200
    assert data["status"] == "healthy"
    
def test_unknown():
    response = client.get("/nope")
    
    data = response.json()
    
    assert response.status_code == 404
    assert {"error"}.issubset(data)
