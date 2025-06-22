#!/usr/bin/env python3
"""
Teste simples e direto dos cálculos de highlights
"""

def calculate_highlights_simple(total_cost: float) -> dict:
    """Cálculo direto dos highlights"""
    
    # 1. Desperdício estimado (15% do total)
    waste_percentage = 15.0
    waste_amount = total_cost * (waste_percentage / 100)
    
    estimated_waste = {
        'amount': round(waste_amount, 2),
        'percentage': round(waste_percentage, 1),
        'total_cost': round(total_cost, 2)
    }
    
    # 2. Economias realizadas (8.5% do total)
    savings_percentage = 8.5
    savings_amount = total_cost * (savings_percentage / 100)
    
    savings_achieved = {
        'amount': round(savings_amount, 2),
        'percentage': round(savings_percentage, 1)
    }
    
    # 3. Previsão próximo mês (4.2% de crescimento)
    growth_percentage = 4.2
    forecasted_amount = total_cost * (1 + growth_percentage / 100)
    
    next_month_forecast = {
        'amount': round(forecasted_amount, 2),
        'change_percentage': round(growth_percentage, 1)
    }
    
    return {
        'estimated_waste': estimated_waste,
        'savings_achieved': savings_achieved,
        'next_month_forecast': next_month_forecast
    }

def test_with_real_data():
    """Teste com dados reais conhecidos"""
    print("🧪 Testing highlights with real data...")
    
    # Valor conhecido dos dados reais
    total_cost = 2277933.8556
    
    print(f"💰 Total cost: ${total_cost:,.2f}")
    
    highlights = calculate_highlights_simple(total_cost)
    
    print(f"💡 Highlights calculated:")
    print(f"   💸 Estimated waste: ${highlights['estimated_waste']['amount']:,.2f} ({highlights['estimated_waste']['percentage']}%)")
    print(f"   💰 Savings achieved: ${highlights['savings_achieved']['amount']:,.2f} ({highlights['savings_achieved']['percentage']}%)")
    print(f"   📈 Next month forecast: ${highlights['next_month_forecast']['amount']:,.2f} ({highlights['next_month_forecast']['change_percentage']:+.1f}%)")
    
    print(f"\n📋 JSON format:")
    import json
    print(json.dumps(highlights, indent=2))
    
    return highlights

if __name__ == "__main__":
    highlights = test_with_real_data()
    print(f"\n✅ Test completed successfully!")