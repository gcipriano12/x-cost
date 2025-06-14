import pytest
from fastapi.testclient import TestClient

def test_login_success(client, admin_user):
    """Teste de login bem-sucedido"""
    login_data = {
        "username": admin_user.username,
        "password": "testpassword"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == admin_user.username
    assert data["user"]["role"] == "admin"

def test_login_invalid_credentials(client):
    """Teste de login com credenciais inválidas"""
    login_data = {
        "username": "nonexistent",
        "password": "wrongpassword"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]

def test_login_inactive_user(client, db_session):
    """Teste de login com usuário inativo"""
    from tests.test_models import User, UserRole
    from tests.test_auth_security import security_manager_test
    
    # Criar usuário inativo
    hashed_password = security_manager_test.get_password_hash("testpassword")
    inactive_user = User(
        username="inactive",
        email="inactive@test.com",
        hashed_password=hashed_password,
        role="viewer",  # String simples para SQLite
        is_active=False
    )
    db_session.add(inactive_user)
    db_session.commit()
    
    login_data = {
        "username": "inactive",
        "password": "testpassword"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    
    assert response.status_code == 401

def test_create_user_as_admin(client, auth_headers):
    """Teste de criação de usuário por admin"""
    user_data = {
        "username": "newuser",
        "email": "newuser@test.com",
        "password": "Password123!",
        "role": "viewer"
    }
    
    response = client.post(
        "/api/v1/auth/users",
        json=user_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@test.com"
    assert data["role"] == "viewer"

def test_create_user_as_non_admin(client, finops_auth_headers):
    """Teste de criação de usuário por não-admin (deve falhar)"""
    user_data = {
        "username": "newuser2",
        "email": "newuser2@test.com",
        "password": "Password123!",
        "role": "viewer"
    }
    
    response = client.post(
        "/api/v1/auth/users",
        json=user_data,
        headers=finops_auth_headers
    )
    
    assert response.status_code == 403

def test_create_duplicate_user(client, auth_headers, admin_user):
    """Teste de criação de usuário duplicado"""
    user_data = {
        "username": admin_user.username,
        "email": "duplicate@test.com",
        "password": "Password123!",
        "role": "viewer"
    }
    
    response = client.post(
        "/api/v1/auth/users",
        json=user_data,
        headers=auth_headers
    )
    
    assert response.status_code == 409  # Conflict para usuário duplicado
    assert "already exists" in response.json()["detail"]

def test_access_protected_endpoint_without_token(client):
    """Teste de acesso a endpoint protegido sem token"""
    response = client.get("/api/v1/credentials")
    
    assert response.status_code == 401

def test_access_protected_endpoint_with_invalid_token(client):
    """Teste de acesso a endpoint protegido com token inválido"""
    headers = {"Authorization": "Bearer invalid_token"}
    
    response = client.get("/api/v1/credentials", headers=headers)
    
    assert response.status_code == 401

def test_access_protected_endpoint_with_valid_token(client, auth_headers):
    """Teste de acesso a endpoint protegido com token válido"""
    response = client.get("/api/v1/credentials", headers=auth_headers)
    
    # Deve retornar 200 (lista vazia) e não 401
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_role_based_access_admin(client, auth_headers):
    """Teste de acesso baseado em role - admin"""
    # Admin deve ter acesso a criação de usuários
    user_data = {
        "username": "roletest",
        "email": "roletest@test.com",
        "password": "Password123!",
        "role": "viewer"
    }
    
    response = client.post(
        "/api/v1/auth/users",
        json=user_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201

def test_role_based_access_viewer(client, viewer_auth_headers):
    """Teste de acesso baseado em role - viewer"""
    # Viewer não deve ter acesso a criação de usuários
    user_data = {
        "username": "roletest2",
        "email": "roletest2@test.com",
        "password": "Password123!",
        "role": "viewer"
    }
    
    response = client.post(
        "/api/v1/auth/users",
        json=user_data,
        headers=viewer_auth_headers
    )
    
    assert response.status_code == 403

def test_password_validation(client, auth_headers):
    """Teste de validação de senha"""
    # Senha muito fraca
    user_data = {
        "username": "weakpass",
        "email": "weakpass@test.com",
        "password": "123",
        "role": "viewer"
    }
    
    response = client.post(
        "/api/v1/auth/users",
        json=user_data,
        headers=auth_headers
    )
    
    assert response.status_code == 422  # Validation error

def test_email_validation(client, auth_headers):
    """Teste de validação de email"""
    # Email inválido
    user_data = {
        "username": "invalidemail",
        "email": "not-an-email",
        "password": "Password123!",
        "role": "viewer"
    }
    
    response = client.post(
        "/api/v1/auth/users",
        json=user_data,
        headers=auth_headers
    )
    
    assert response.status_code == 422  # Validation error