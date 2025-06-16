#!/usr/bin/env python3
"""
Teste específico para a nova implementação do get_aws_savings
"""

import asyncio
import logging
from app.cloud_native_optimization import AWSOptimizationService

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_aws_savings_method():
    """Testa o método get_aws_savings especificamente"""
    
    print("🧪 Testando novo método get_aws_savings...")
    
    try:
        # Criar instância do serviço AWS (sem credenciais reais)
        aws_service = AWSOptimizationService()
        print("✅ AWSOptimizationService criado")
        
        # Testar se o método existe e pode ser chamado
        print("🔍 Testando método get_aws_savings...")
        
        # Como não temos credenciais AWS reais, isto deve falhar graciosamente
        try:
            savings = await aws_service.get_aws_savings(min_savings=10.0)
            print(f"✅ get_aws_savings executado: {len(savings)} oportunidades")
        except Exception as e:
            if "credentials" in str(e).lower() or "unauthorized" in str(e).lower():
                print("⚠️ Método existe mas falhou por falta de credenciais (esperado)")
                print(f"   Erro: {e}")
            else:
                print(f"❌ Erro inesperado: {e}")
                raise
        
        # Testar método get_savings_opportunities (deve usar get_aws_savings)
        print("🔍 Testando método get_savings_opportunities...")
        try:
            savings = await aws_service.get_savings_opportunities()
            print(f"✅ get_savings_opportunities executado: {len(savings)} oportunidades")
        except Exception as e:
            if "credentials" in str(e).lower() or "unauthorized" in str(e).lower():
                print("⚠️ Método existe mas falhou por falta de credenciais (esperado)")
                print(f"   Erro: {e}")
            else:
                print(f"❌ Erro inesperado: {e}")
                raise
        
        print("✅ Testes do método get_aws_savings concluídos!")
        
    except ImportError as e:
        print(f"⚠️ boto3 não disponível: {e}")
        print("   Execute: pip install boto3")
    except Exception as e:
        print(f"❌ Erro ao criar serviço AWS: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_aws_savings_method())
