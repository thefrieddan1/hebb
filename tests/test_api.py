import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_search_routes_no_filter():
    response = client.post("/routes/search", json={})
    assert response.status_code == 200
    data = response.json()
    assert len(data["nodes"]) > 0
    assert len(data["edges"]) > 0

def test_search_routes_start_public():
    query = {
        "start_filters": [{"field": "publicExposed", "operator": "eq", "value": True}]
    }
    response = client.post("/routes/search", json=query)
    assert response.status_code == 200
    data = response.json()
    assert len(data["nodes"]) > 0

def test_search_routes_end_sink():
    query = {
        "end_filters": [{"field": "kind", "operator": "in", "value": ["rds", "sqs"]}]
    }
    response = client.post("/routes/search", json=query)
    assert response.status_code == 200
    data = response.json()
    assert len(data["nodes"]) > 0

def test_search_routes_vuln_and_sink():
    # This should return paths from vulnerable nodes to sink
    query = {
        "end_filters": [{"field": "kind", "operator": "in", "value": ["rds", "sqs"]}],
        "path_filters": [{"field": "vulnerabilities", "operator": "neq", "value": None}]
    }
    response = client.post("/routes/search", json=query)
    assert response.status_code == 200
    data = response.json()
    assert len(data["nodes"]) > 0

def test_search_routes_public_and_sink():
    # This should return empty as per debug analysis
    query = {
        "start_filters": [{"field": "publicExposed", "operator": "eq", "value": True}],
        "end_filters": [{"field": "kind", "operator": "in", "value": ["rds", "sqs"]}]
    }
    response = client.post("/routes/search", json=query)
    assert response.status_code == 200
    data = response.json()
    assert len(data["nodes"]) == 0

def test_search_routes_generic_language():
    # New test for generic capability: Filter by language = java
    query = {
        "start_filters": [{"field": "language", "operator": "eq", "value": "java"}]
    }
    response = client.post("/routes/search", json=query)
    assert response.status_code == 200
    data = response.json()
    # Most services are java, so should get results
    assert len(data["nodes"]) > 0

