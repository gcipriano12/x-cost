import pytest
from fastapi.testclient import TestClient
from .test_config import test_app

@pytest.fixture
def client():
    """Cliente de teste"""
    return TestClient(test_app)

def test_login_success(client, admin_user):
    """Testa login com credenciais válidas"""
    response = client.post("/api/v1/auth/login", json={
        "username": "testadmin",
        "password": "testpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_failure(client):
    """Testa login com credenciais inválidas"""
    response = client.post("/api/v1/auth/login", json={
        "username": "invalid_user",
        "password": "wrong_password"
    })
    assert response.status_code == 401

def test_get_credentials(client, admin_auth_headers):
    """Testa listagem de credenciais"""
    response = client.get("/api/v1/credentials", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_create_credentials(client, admin_auth_headers, sample_aws_credentials):
    """Testa criação de credenciais"""
    response = client.post(
        "/api/v1/credentials",
        json=sample_aws_credentials,
        headers=admin_auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == sample_aws_credentials["name"]
    assert data["provider_type"] == sample_aws_credentials["provider_type"]

def test_get_single_credential(client, admin_auth_headers):
    """Testa obtenção de uma credencial específica"""
    # Primeiro criar uma credencial
    response = client.post(
        "/api/v1/credentials",
        json={
            "name": "test-credential",
            "provider_type": "AWS",
            "credentials": {
                "access_key_id": "AKIATEST12345678901",
                "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                "region": "us-east-1",
                "account_id": "123456789012"
            }
        },
        headers=admin_auth_headers
    )
    assert response.status_code == 201
    created_data = response.json()
    
    # Agora buscar a credencial criada
    response = client.get(
        f"/api/v1/credentials/{created_data['id']}",
        headers=admin_auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_data["id"]
    assert data["name"] == "test-credential"

def test_update_credential(client, admin_auth_headers):
    """Testa atualização de credenciais"""
    # Primeiro criar uma credencial
    response = client.post(
        "/api/v1/credentials",
        json={
            "name": "test-credential-update",
            "provider_type": "AWS",
            "credentials": {
                "access_key_id": "AKIATEST12345678901",
                "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                "region": "us-east-1",
                "account_id": "123456789012"
            }
        },
        headers=admin_auth_headers
    )
    assert response.status_code == 201
    created_data = response.json()
    
    # Atualizar a credencial
    update_data = {
        "name": "updated-credential",
        "description": "Updated description"
    }
    response = client.put(
        f"/api/v1/credentials/{created_data['id']}",
        json=update_data,
        headers=admin_auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "updated-credential"
    assert data["description"] == "Updated description"

def test_delete_credential(client, admin_auth_headers):
    """Testa deleção de credenciais"""
    # Primeiro criar uma credencial
    response = client.post(
        "/api/v1/credentials",
        json={
            "name": "test-credential-delete",
            "provider_type": "AWS",
            "credentials": {
                "access_key_id": "AKIATEST12345678901",
                "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                "region": "us-east-1",
                "account_id": "123456789012"
            }
        },
        headers=admin_auth_headers
    )
    assert response.status_code == 201
    created_data = response.json()
    
    # Deletar a credencial
    response = client.delete(
        f"/api/v1/credentials/{created_data['id']}",
        headers=admin_auth_headers
    )
    assert response.status_code == 204
    
    # Verificar que foi realmente deletada
    response = client.get(
        f"/api/v1/credentials/{created_data['id']}",
        headers=admin_auth_headers
    )
    assert response.status_code == 404

def test_validate_credential(client, admin_auth_headers):
    """Testa validação de credenciais"""
    # Primeiro criar uma credencial
    response = client.post(
        "/api/v1/credentials",
        json={
            "name": "test-credential-validate",
            "provider_type": "AWS",
            "credentials": {
                "access_key_id": "AKIATEST12345678901",
                "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                "region": "us-east-1",
                "account_id": "123456789012"
            }
        },
        headers=admin_auth_headers
    )
    assert response.status_code == 201
    created_data = response.json()
    
    # Validar a credencial
    response = client.post(
        f"/api/v1/credentials/{created_data['id']}/validate",
        headers=admin_auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True

def test_test_credential(client, admin_auth_headers, sample_aws_credentials):
    """Testa teste de credenciais sem salvar"""
    response = client.post(
        "/api/v1/credentials/test",
        json=sample_aws_credentials,
        headers=admin_auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "is_valid" in data
