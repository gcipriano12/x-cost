import pytest
from unittest.mock import patch

def test_create_aws_credentials(client, finops_auth_headers, sample_aws_credentials, mock_secrets_manager):
    """Teste de criação de credenciais AWS"""
    response = client.post(
        "/api/v1/credentials",
        json=sample_aws_credentials,
        headers=finops_auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sample_aws_credentials["name"]
    assert data["provider_type"] == "AWS"
    assert data["status"] == "active"
    assert "id" in data

def test_create_azure_credentials(client, finops_auth_headers, sample_azure_credentials, mock_secrets_manager):
    """Teste de criação de credenciais Azure"""
    response = client.post(
        "/api/v1/credentials",
        json=sample_azure_credentials,
        headers=finops_auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sample_azure_credentials["name"]
    assert data["provider_type"] == "Azure"

def test_create_credentials_without_permission(client, viewer_auth_headers, sample_aws_credentials):
    """Teste de criação de credenciais sem permissão"""
    response = client.post(
        "/api/v1/credentials",
        json=sample_aws_credentials,
        headers=viewer_auth_headers
    )
    
    assert response.status_code == 403

def test_create_duplicate_credentials(client, finops_auth_headers, sample_aws_credentials, mock_secrets_manager):
    """Teste de criação de credenciais duplicadas"""
    # Criar primeira credencial
    response1 = client.post(
        "/api/v1/credentials",
        json=sample_aws_credentials,
        headers=finops_auth_headers
    )
    assert response1.status_code == 201
    
    # Tentar criar duplicata
    response2 = client.post(
        "/api/v1/credentials",
        json=sample_aws_credentials,
        headers=finops_auth_headers
    )
    assert response2.status_code == 409

def test_list_credentials(client, finops_auth_headers, sample_aws_credentials, mock_secrets_manager):
    """Teste de listagem de credenciais"""
    # Criar algumas credenciais
    client.post("/api/v1/credentials", json=sample_aws_credentials, headers=finops_auth_headers)
    
    azure_creds = {
        "name": "test-azure",
        "provider_type": "Azure",
        "credentials": {
            "subscription_id": "12345678-1234-1234-1234-123456789012",
            "client_id": "12345678-1234-1234-1234-123456789012",
            "client_secret": "test-secret",
            "tenant_id": "12345678-1234-1234-1234-123456789012"
        }
    }
    client.post("/api/v1/credentials", json=azure_creds, headers=finops_auth_headers)
    
    # Listar todas
    response = client.get("/api/v1/credentials", headers=finops_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_list_credentials_with_filters(client, finops_auth_headers, sample_aws_credentials, mock_secrets_manager):
    """Teste de listagem com filtros"""
    # Criar credencial
    client.post("/api/v1/credentials", json=sample_aws_credentials, headers=finops_auth_headers)
    
    # Filtrar por provedor
    response = client.get(
        "/api/v1/credentials?provider_type=AWS",
        headers=finops_auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["provider_type"] == "AWS"

def test_get_specific_credential(client, finops_auth_headers, sample_aws_credentials, mock_secrets_manager):
    """Teste de obtenção de credencial específica"""
    # Criar credencial
    create_response = client.post(
        "/api/v1/credentials",
        json=sample_aws_credentials,
        headers=finops_auth_headers
    )
    credential_id = create_response.json()["id"]
    
    # Obter credencial específica
    response = client.get(
        f"/api/v1/credentials/{credential_id}",
        headers=finops_auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == credential_id
    assert data["name"] == sample_aws_credentials["name"]

def test_get_nonexistent_credential(client, finops_auth_headers):
    """Teste de obtenção de credencial inexistente"""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(
        f"/api/v1/credentials/{fake_id}",
        headers=finops_auth_headers
    )
    assert response.status_code == 404

def test_update_credential(client, finops_auth_headers, sample_aws_credentials, mock_secrets_manager):
    """Teste de atualização de credencial"""
    # Criar credencial
    create_response = client.post(
        "/api/v1/credentials",
        json=sample_aws_credentials,
        headers=finops_auth_headers
    )
    credential_id = create_response.json()["id"]
    
    # Atualizar
    update_data = {
        "name": "updated-aws-account",
        "description": "Updated description"
    }
    
    response = client.put(
        f"/api/v1/credentials/{credential_id}",
        json=update_data,
        headers=finops_auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "updated-aws-account"
    assert data["description"] == "Updated description"

def test_delete_credential(client, finops_auth_headers, sample_aws_credentials, mock_secrets_manager):
    """Teste de remoção de credencial"""
    # Criar credencial
    create_response = client.post(
        "/api/v1/credentials",
        json=sample_aws_credentials,
        headers=finops_auth_headers
    )
    credential_id = create_response.json()["id"]
    
    # Remover
    response = client.delete(
        f"/api/v1/credentials/{credential_id}",
        headers=finops_auth_headers
    )
    assert response.status_code == 204
    
    # Verificar que foi removida
    get_response = client.get(
        f"/api/v1/credentials/{credential_id}",
        headers=finops_auth_headers
    )
    assert get_response.status_code == 404

def test_validate_credential(client, finops_auth_headers, sample_aws_credentials, mock_secrets_manager):
    """Teste de validação de credencial"""
    # Criar credencial
    create_response = client.post(
        "/api/v1/credentials",
        json=sample_aws_credentials,
        headers=finops_auth_headers
    )
    credential_id = create_response.json()["id"]
    
    # Validar
    response = client.post(
        f"/api/v1/credentials/{credential_id}/validate",
        headers=finops_auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] == True
    assert data["provider_type"] == "AWS"

def test_test_credentials_without_saving(client, finops_auth_headers, mock_secrets_manager):
    """Teste de credenciais sem salvar"""
    test_data = {
        "provider_type": "AWS",
        "credentials": {
            "access_key_id": "AKIAIOSFODNN7EXAMPLE",
            "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            "region": "us-east-1",
            "account_id": "123456789012"
        }
    }
    
    response = client.post(
        "/api/v1/credentials/test",
        json=test_data,
        headers=finops_auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] == True

def test_invalid_credential_format(client, finops_auth_headers):
    """Teste de formato inválido de credencial"""
    invalid_aws_creds = {
        "name": "invalid-aws",
        "provider_type": "AWS",
        "credentials": {
            "access_key_id": "INVALID",  # Formato inválido
            "secret_access_key": "short",  # Muito curto
            "region": "us-east-1"
        }
    }
    
    response = client.post(
        "/api/v1/credentials",
        json=invalid_aws_creds,
        headers=finops_auth_headers
    )
    assert response.status_code == 422  # Validation error

def test_credentials_without_authentication(client, sample_aws_credentials):
    """Teste de operações com credenciais sem autenticação"""
    # Criar
    response = client.post("/api/v1/credentials", json=sample_aws_credentials)
    assert response.status_code == 401
    
    # Listar
    response = client.get("/api/v1/credentials")
    assert response.status_code == 401
    
    # Obter específica
    response = client.get("/api/v1/credentials/fake-id")
    assert response.status_code == 401

def test_credential_expiration(client, finops_auth_headers, mock_secrets_manager):
    """Teste de credencial com expiração"""
    from datetime import datetime, timedelta
    
    expiring_creds = {
        "name": "expiring-aws",
        "provider_type": "AWS",
        "credentials": {
            "access_key_id": "AKIAIOSFODNN7EXAMPLE",
            "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            "region": "us-east-1"
        },
        "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
    }
    
    response = client.post(
        "/api/v1/credentials",
        json=expiring_creds,
        headers=finops_auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["expires_at"] is not None

def test_credential_status_management(client, finops_auth_headers, sample_aws_credentials, mock_secrets_manager):
    """Teste de gerenciamento de status de credencial"""
    # Criar credencial
    create_response = client.post(
        "/api/v1/credentials",
        json=sample_aws_credentials,
        headers=finops_auth_headers
    )
    credential_id = create_response.json()["id"]
    
    # Desativar
    update_data = {"status": "inactive"}
    response = client.put(
        f"/api/v1/credentials/{credential_id}",
        json=update_data,
        headers=finops_auth_headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "inactive"
    
    # Filtrar por status
    response = client.get(
        "/api/v1/credentials?status=active",
        headers=finops_auth_headers
    )
    assert response.status_code == 200
    # Não deve incluir a credencial inativa
    active_creds = response.json()
    assert len([c for c in active_creds if c["id"] == credential_id]) == 0