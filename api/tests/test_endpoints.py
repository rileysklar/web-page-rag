"""
Tests for API endpoints.
"""
import pytest
from fastapi import status

@pytest.mark.unit
def test_health_check(test_client):
    """Test health check endpoint."""
    response = test_client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy"}

@pytest.mark.unit
def test_query_without_api_key(test_client, sample_question):
    """Test query endpoint without API key."""
    response = test_client.post(
        "/api/rag/query",
        json={"question": sample_question}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.unit
def test_query_with_api_key(test_client, api_key_headers, sample_question):
    """Test query endpoint with API key."""
    response = test_client.post(
        "/api/rag/query",
        headers=api_key_headers,
        json={
            "question": sample_question,
            "namespace": "test"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "answer" in data
    assert "sources" in data

@pytest.mark.unit
def test_index_without_api_key(test_client, sample_url):
    """Test index endpoint without API key."""
    response = test_client.post(
        "/api/rag/index",
        json={"url": sample_url}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.unit
def test_index_with_api_key(test_client, api_key_headers, sample_url):
    """Test index endpoint with API key."""
    response = test_client.post(
        "/api/rag/index",
        headers=api_key_headers,
        json={
            "url": sample_url,
            "namespace": "test"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "started"
    assert "task_id" in data

@pytest.mark.unit
def test_index_status_without_api_key(test_client):
    """Test index status endpoint without API key."""
    response = test_client.get("/api/rag/index/test-task-id")
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.unit
def test_index_status_with_api_key(test_client, api_key_headers):
    """Test index status endpoint with API key."""
    # First create an indexing task
    index_response = test_client.post(
        "/api/rag/index",
        headers=api_key_headers,
        json={
            "url": "https://example.com",
            "namespace": "test"
        }
    )
    task_id = index_response.json()["task_id"]
    
    # Then check its status
    response = test_client.get(
        f"/api/rag/index/{task_id}",
        headers=api_key_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "status" in data
    assert "progress" in data 