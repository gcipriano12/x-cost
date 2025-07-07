#!/usr/bin/env python3
import sys
import os
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Budget

engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://finops_user:finops_password@localhost:5432/finops_db'))
Session = sessionmaker(bind=engine)
db = Session()

print('📊 Todos os budgets ativos:')
budgets = db.query(Budget).filter(Budget.is_active == True).order_by(Budget.provider_name).all()
for budget in budgets:
    amount = float(budget.budget_amount)
    print(f'  - {budget.budget_name}: provider={budget.provider_name}, amount=${amount:,.2f}')

db.close()
