#!/usr/bin/env python3
"""
Teste direto dos highlights sem servidor
"""

import sys
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

from datetime import date, timedelta
from app.cost_analytics.dashboard.dashboard_analyzer import DashboardAnalyzer
from app.database import get_database

# Simular sessão de banco
class MockDB:
    def execute(self, query, params):
        # Simular resultado com custo real conhecido
        class MockResult:
            def fetchone(self):
                return [2277933.8556]  # Valor conhecido dos dados reais
        return MockResult()

def test_highlights():
    """Testar diretamente os highlights"""
    print("🧪 Testing highlights calculation...")
    
    # Criar analyzer com mock DB
    mock_db = MockDB()
    analyzer = DashboardAnalyzer(mock_db)
    
    # Definir período
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    print(f"📅 Period: {start_date} to {end_date}")
    
    # Testar cálculo de highlights
    highlights = analyzer._calculate_highlights(start_date, end_date)
    
    print(f"💡 Highlights calculated:")
    print(f"   💸 Estimated waste: ${highlights['estimated_waste']['amount']:,.2f} ({highlights['estimated_waste']['percentage']}%)")
    print(f"   💰 Savings achieved: ${highlights['savings_achieved']['amount']:,.2f} ({highlights['savings_achieved']['percentage']}%)")
    print(f"   📈 Next month forecast: ${highlights['next_month_forecast']['amount']:,.2f} ({highlights['next_month_forecast']['change_percentage']:+.1f}%)")
    
    return highlights

if __name__ == "__main__":
    highlights = test_highlights()
    print(f"✅ Test completed successfully!")
    print(f"📊 Full result: {highlights}")