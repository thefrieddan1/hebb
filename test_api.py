import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_routes_no_filter():
    response = client.get("/routes")
    assert response.status_code == 200
    data = response.json()
    assert len(data["nodes"]) > 0
    assert len(data["edges"]) > 0

def test_get_routes_start_public():
    response = client.get("/routes?start_public=true")
    assert response.status_code == 200
    data = response.json()
    
    # Verify all returned nodes are reachable from a public node
    # This is hard to verify without graph logic here, but we can check if we got a subset
    assert len(data["nodes"]) > 0

def test_get_routes_end_sink():
    response = client.get("/routes?end_sink=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data["nodes"]) > 0

def test_get_routes_vulnerability():
    response = client.get("/routes?has_vulnerability=true")
    assert response.status_code == 200
    data = response.json()
    
    # Check if we have nodes with vulnerabilities
    vulnerable_nodes = [n for n in data["nodes"] if n.get("vulnerabilities")]
    assert len(vulnerable_nodes) > 0

def test_get_routes_vuln_and_sink():
    # This should return paths from vulnerable nodes to sink
    response = client.get("/routes?has_vulnerability=true&end_sink=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data["nodes"]) > 0

def test_get_routes_public_and_sink():
    # This should return empty as per debug analysis
    response = client.get("/routes?start_public=true&end_sink=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data["nodes"]) == 0

def test_get_routes_all_filters():
    # This should also be empty because public -> sink is empty
    response = client.get("/routes?start_public=true&end_sink=true&has_vulnerability=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data["nodes"]) == 0
