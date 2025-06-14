"""
Este arquivo importa todos os fixtures necessários para os testes.
"""
import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao PYTHONPATH
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

# Importar fixtures do test_config.py diretamente
from .test_config import (
    client, db_session, admin_user, finops_admin_user, admin_auth_headers,
    finops_auth_headers, viewer_auth_headers, admin_user_data, test_user_data, aws_credential_data,
    azure_credential_data, sample_aws_credentials, sample_azure_credentials,
    mock_secrets_manager, auth_headers, credential_data
)
