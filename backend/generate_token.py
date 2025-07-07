#!/usr/bin/env python3
"""
Script para gerar um novo token de autenticação
"""

import sys
import os
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

from app.auth_security import SecurityManager
from datetime import timedelta

def generate_new_token():
    """Gerar um novo token válido"""
    
    print("🔑 GERANDO NOVO TOKEN DE AUTENTICAÇÃO")
    print("=" * 50)
    
    try:
        # Instanciar o gerenciador de segurança
        security_manager = SecurityManager()
        
        # Dados do usuário admin
        user_data = {
            "sub": "finops_admin",
            "role": "finops_admin"
        }
        
        # Gerar token com 24 horas de validade
        token = security_manager.create_access_token(
            data=user_data,
            expires_delta=timedelta(hours=24)
        )
        
        print(f"✅ Novo token gerado com sucesso:")
        print(f"Token: {token}")
        print(f"\n🔧 Para usar em curl:")
        print(f'curl -H "Authorization: Bearer {token}" "http://localhost:8000/api/v1/dashboard/summary?start_date=2025-06-06&end_date=2025-07-06"')
        
        return token
        
    except Exception as e:
        print(f"❌ Erro ao gerar token: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    generate_new_token()
