#!/usr/bin/env python3
"""
Script para testar credenciais no banco
"""
import os
import sys
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.credential_models import User
from app.auth_security import security_manager

def test_credentials():
    """Testar credenciais conhecidas"""
    engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://finops_user:finops_password@localhost:5432/finops_db'))
    Session = sessionmaker(bind=engine)
    db = Session()

    # Testar senhas conhecidas para usuários admin
    test_passwords = ['TestPass123!', 'ChangeMe123!', 'Password123!', 'admin', 'test', 'testpassword']
    admin_users = ['admin', 'test', 'testadmin', 'finops_admin']

    print('Testando credenciais:')
    for username in admin_users:
        user = db.query(User).filter(User.username == username).first()
        if user:
            print(f'\nTestando usuário: {username}')
            for password in test_passwords:
                if security_manager.verify_password(password, user.hashed_password):
                    print(f'✅ SUCESSO: {username} / {password}')
                    break
            else:
                print(f'❌ Nenhuma senha funcionou para {username}')

    db.close()

if __name__ == "__main__":
    test_credentials()
