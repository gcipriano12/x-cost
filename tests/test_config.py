import pytest
import asyncio
import sys
import os
from pathlib import Path
from contextlib import asynccontextmanager

# É MUITO importante definir DATABASE_URL antes de qualquer importação da aplicação
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

# Importações necessárias
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi import FastAPI
from fastapi.testclient import TestClient

app_path = Path(__file__).parent.parent / "app"
sys.path.append(str(app_path))

# URL do banco de teste
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Engine de teste
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Importamos os modelos de teste sem schema
from tests.test_models import TestBase, User, UserRole, CloudCredential, CloudProvider

# Definir uma sessão de teste
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def get_test_database():
    """Dependency override para usar banco de teste"""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Criar uma aplicação de teste simples
@asynccontextmanager
async def app_lifespan(_: FastAPI):
    """Lifespan para aplicação de teste"""
    # Startup
    TestBase.metadata.create_all(bind=test_engine)
    yield
    # Shutdown
    TestBase.metadata.drop_all(bind=test_engine)

# Aplicação de teste mínima
test_app = FastAPI(
    title="X Cost API - Test",
    description="API para gerenciamento de credenciais FinOps - Testes",
    version="1.0.0",
    lifespan=app_lifespan
)

# Override das dependências para usar banco de teste
from app.database import get_database
test_app.dependency_overrides[get_database] = get_test_database

# Importações para criar as rotas de teste
from tests.test_credentials_api import credentials_router_test, auth_router_test, audit_router_test
# Usar versão de teste do SecurityManager no lugar do original
from tests.test_auth_security import security_manager_test as security_manager

# Adicionar rotas de teste
test_app.include_router(credentials_router_test, tags=["credentials"])
test_app.include_router(auth_router_test, tags=["auth"])  
test_app.include_router(audit_router_test, tags=["audit"])

# Sobrescrever dependências relacionadas ao security_manager
import app.auth_security
app.auth_security.security_manager = security_manager

@pytest.fixture(scope="session")
def event_loop():
    """Criar event loop para testes async"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session():
    """Criar sessão de banco de dados para teste"""
    # Limpar e criar tabelas para cada teste
    TestBase.metadata.drop_all(bind=test_engine)
    TestBase.metadata.create_all(bind=test_engine)
    
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client():
    """Criar cliente de teste"""
    with TestClient(test_app) as test_client:
        yield test_client

@pytest.fixture
def admin_user(db_session):
    """Criar usuário admin para testes"""
    hashed_password = security_manager.get_password_hash("testpassword")
    user = User(
        username="testadmin",
        email="admin@test.com",
        hashed_password=hashed_password,
        role="admin",  # String simples para SQLite
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def finops_admin_user(db_session):
    """Criar usuário finops admin para testes"""
    hashed_password = security_manager.get_password_hash("testpassword")
    user = User(
        username="testfinops",
        email="finops@test.com",
        hashed_password=hashed_password,
        role="finops_admin",  # String simples para SQLite
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def admin_auth_headers(client, admin_user):
    """Headers de autenticação para admin"""
    login_data = {
        "username": admin_user.username,
        "password": "testpassword"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def finops_auth_headers(client, finops_admin_user):
    """Headers de autenticação para finops admin"""
    login_data = {
        "username": finops_admin_user.username,
        "password": "testpassword"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_user_data():
    """Dados de usuário admin para testes"""
    return {
        "username": "admin",
        "email": "admin@example.com", 
        "password": "SecurePass123!",
        "role": "admin"
    }

@pytest.fixture  
def test_user_data():
    """Dados de usuário comum para testes"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123!",
        "role": "viewer"
    }

@pytest.fixture
def aws_credential_data():
    """Dados de credencial AWS para testes"""
    return {
        "name": "test-aws-cred",
        "provider_type": "aws",
        "description": "Test AWS credentials",
        "access_key_id": "AKIATEST12345678901",
        "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    }

@pytest.fixture
def azure_credential_data():
    """Dados de credencial Azure para testes"""
    return {
        "name": "test-azure-cred", 
        "provider_type": "azure",
        "description": "Test Azure credentials",
        "client_id": "12345678-1234-1234-1234-123456789012",
        "client_secret": "test-secret-value",
        "tenant_id": "87654321-4321-4321-4321-210987654321"
    }

@pytest.fixture
def sample_aws_credentials():
    """Credenciais AWS de exemplo para testes"""
    return {
        "name": "test-aws-account",
        "description": "Test AWS credentials",
        "provider_type": "AWS",
        "credentials": {
            "access_key_id": "AKIAIOSFODNN7EXAMPLE",
            "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            "region": "us-east-1",
            "account_id": "123456789012"
        }
    }

@pytest.fixture
def sample_azure_credentials():
    """Credenciais Azure de exemplo para testes"""
    return {
        "name": "test-azure-subscription",
        "description": "Test Azure credentials",
        "provider_type": "Azure",
        "credentials": {
            "subscription_id": "12345678-1234-1234-1234-123456789012",
            "client_id": "12345678-1234-1234-1234-123456789012",
            "client_secret": "test-client-secret",
            "tenant_id": "12345678-1234-1234-1234-123456789012"
        }
    }

# Mock para o SecretsManager
class MockSecretsManager:
    def __init__(self):
        self.secrets = {}
    
    def store_credentials(self, credential_name, provider_type, credentials, description=None, expires_at=None):
        secret_name = f"test/{provider_type.lower()}/{credential_name}"
        secret_arn = f"arn:aws:secretsmanager:us-east-1:123456789012:secret:{secret_name}"
        
        self.secrets[secret_arn] = {
            "provider_type": provider_type,
            "credential_name": credential_name,
            "credentials": credentials,
            "created_at": "2025-06-03T10:00:00Z"
        }
        
        return secret_arn, secret_name
    
    def retrieve_credentials(self, secret_arn):
        if secret_arn not in self.secrets:
            raise ValueError("Credentials not found")
        return self.secrets[secret_arn]
    
    def update_credentials(self, secret_arn, credentials, description=None):
        if secret_arn not in self.secrets:
            raise ValueError("Credentials not found")
        self.secrets[secret_arn]["credentials"] = credentials
        return True
    
    def delete_credentials(self, secret_arn, force_delete=False):
        if secret_arn in self.secrets:
            del self.secrets[secret_arn]
        return True
    
    def validate_credentials(self, secret_arn):
        if secret_arn not in self.secrets:
            raise ValueError("Credentials not found")
        
        # Mock de validação sempre bem-sucedida para testes
        return {
            "is_valid": True,
            "provider_type": self.secrets[secret_arn]["provider_type"],
            "validation_timestamp": "2025-06-03T10:00:00Z",
            "account_info": {"account_id": "123456789012"},
            "permissions_check": {"cost_explorer": True}
        }

@pytest.fixture
def mock_secrets_manager(monkeypatch):
    """Mock do Secrets Manager para testes"""
    mock_sm = MockSecretsManager()
    
    # Função que retorna nosso mock
    def get_mock_secrets_manager():
        return mock_sm
    
    # Substituir a função get_secrets_manager
    from app.secrets_manager import get_secrets_manager
    monkeypatch.setattr("app.secrets_manager.get_secrets_manager", get_mock_secrets_manager)
    
    return mock_sm

@pytest.fixture
def viewer_auth_headers(client, db_session):
    """Headers de autenticação para usuário viewer"""
    # Criar usuário viewer
    hashed_password = security_manager.get_password_hash("testpassword")
    user = User(
        username="testviewer",
        email="viewer@test.com",
        hashed_password=hashed_password,
        role="viewer",  # String simples para SQLite
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    login_data = {
        "username": user.username,
        "password": "testpassword"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# Aliases para compatibilidade com testes existentes
@pytest.fixture
def auth_headers(admin_auth_headers):
    """Alias para admin_auth_headers"""
    return admin_auth_headers

@pytest.fixture
def credential_data():
    """Dados de credencial de teste"""
    return {
        "name": "test-credential",
        "provider_type": "AWS",
        "description": "Test credential for testing",
        "credentials": {
            "access_key_id": "AKIAIOSFODNN7EXAMPLE",
            "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            "region": "us-east-1",
            "account_id": "123456789012"
        }
    }