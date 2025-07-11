import pytest
from unittest.mock import Mock, patch, MagicMock
from app.credentials.strategies.aws_strategy import AWSCredentialStrategy
from app.credentials.strategies.base import AccessPattern, CredentialType
from app.credentials.strategies.factory import CredentialStrategyFactory

class TestAWSCredentialStrategy:
    
    def test_hybrid_strategy_initialization(self):
        """Testar inicialização da estratégia híbrida"""
        config = {
            'access_key_id': 'test_key',
            'secret_access_key': 'test_secret',
            'region': 'us-east-1'
        }
        
        with patch('boto3.Session'):
            strategy = AWSCredentialStrategy(AccessPattern.HYBRID, config)
            
            assert strategy.access_pattern == AccessPattern.HYBRID
            assert strategy.config == config
    
    @patch('boto3.Session')
    def test_data_client_creation(self, mock_session):
        """Testar criação de cliente para dados"""
        config = {
            'access_key_id': 'test_key',
            'secret_access_key': 'test_secret',
            'region': 'us-east-1'
        }
        
        # Mock da sessão e cliente
        mock_session_instance = MagicMock()
        mock_client = MagicMock()
        mock_session_instance.client.return_value = mock_client
        mock_session.return_value = mock_session_instance
        
        strategy = AWSCredentialStrategy(AccessPattern.DATA_ONLY, config)
        client = strategy.get_data_client('s3')
        
        assert client is not None
        mock_session.assert_called()
        mock_session_instance.client.assert_called_with('s3')
    
    def test_compatibility_with_patterns(self):
        """Testar compatibilidade com padrões"""
        config = {'access_key_id': 'test', 'secret_access_key': 'test'}
        
        with patch('boto3.Session'):
            strategy = AWSCredentialStrategy(AccessPattern.HYBRID, config)
            
            assert strategy.is_compatible_with_pattern(AccessPattern.DATA_ONLY)
            assert strategy.is_compatible_with_pattern(AccessPattern.API_ONLY)
            assert strategy.is_compatible_with_pattern(AccessPattern.HYBRID)
    
    @patch('boto3.Session')
    @patch('boto3.client')
    def test_role_assumption_for_data_access(self, mock_boto_client, mock_session):
        """Testar assunção de role para acesso a dados"""
        config = {
            'access_key_id': 'test_key',
            'secret_access_key': 'test_secret',
            'region': 'us-east-1',
            'data_role_arn': 'arn:aws:iam::123456789012:role/DataAccessRole'
        }
        
        # Mock do STS assume_role
        mock_sts = MagicMock()
        mock_sts.assume_role.return_value = {
            'Credentials': {
                'AccessKeyId': 'assumed_key',
                'SecretAccessKey': 'assumed_secret',
                'SessionToken': 'session_token'
            }
        }
        mock_boto_client.return_value = mock_sts
        
        # Mock da sessão assumida
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        strategy = AWSCredentialStrategy(AccessPattern.DATA_ONLY, config)
        
        # Verificar se assume_role foi chamado
        mock_sts.assume_role.assert_called_with(
            RoleArn=config['data_role_arn'],
            RoleSessionName='xcost-data-access'
        )
        
        # Verificar se sessão foi criada com credenciais assumidas
        mock_session.assert_called_with(
            aws_access_key_id='assumed_key',
            aws_secret_access_key='assumed_secret',
            aws_session_token='session_token',
            region_name='us-east-1'
        )

class TestCredentialStrategyFactory:
    
    def test_factory_registration(self):
        """Testar registro de estratégias no factory"""
        # Verificar se AWS foi registrada
        supported = CredentialStrategyFactory.get_supported_providers()
        assert "AWS" in supported
    
    def test_strategy_creation(self):
        """Testar criação de estratégia via factory"""
        config = {
            'access_key_id': 'test',
            'secret_access_key': 'test',
            'region': 'us-east-1'
        }
        
        with patch('boto3.Session'):
            strategy = CredentialStrategyFactory.create_strategy(
                provider="AWS",
                access_pattern=AccessPattern.HYBRID,
                credential_config=config
            )
            
            assert isinstance(strategy, AWSCredentialStrategy)
            assert strategy.access_pattern == AccessPattern.HYBRID
    
    def test_unsupported_provider(self):
        """Testar erro para provedor não suportado"""
        config = {'test': 'config'}
        
        with pytest.raises(ValueError, match="Provider UNSUPPORTED not supported"):
            CredentialStrategyFactory.create_strategy(
                provider="UNSUPPORTED",
                access_pattern=AccessPattern.HYBRID,
                credential_config=config
            )

class TestAccessPatterns:
    
    def test_access_pattern_enum_values(self):
        """Testar valores do enum AccessPattern"""
        assert AccessPattern.DATA_ONLY.value == "data_only"
        assert AccessPattern.API_ONLY.value == "api_only"
        assert AccessPattern.HYBRID.value == "hybrid"
    
    def test_credential_type_enum_values(self):
        """Testar valores do enum CredentialType"""
        assert CredentialType.ROLE_BASED.value == "role_based"
        assert CredentialType.PROGRAMMATIC.value == "programmatic"
        assert CredentialType.SERVICE_ACCOUNT.value == "service_account"
