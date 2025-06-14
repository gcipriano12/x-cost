#!/usr/bin/env python3
"""
Query SQL para calcular totais de 2024
"""

from app.database import SessionLocal
from sqlalchemy import text

def main():
    db = SessionLocal()
    try:
        # Query SQL para calcular o total de 2024
        query = """
        SELECT 
            COUNT(*) as total_records,
            SUM(effective_cost) as total_cost_2024,
            AVG(effective_cost) as average_cost,
            MIN(effective_cost) as min_cost,
            MAX(effective_cost) as max_cost,
            MIN(billing_period_start) as first_date,
            MAX(billing_period_start) as last_date
        FROM focus_cost_data 
        WHERE EXTRACT(YEAR FROM billing_period_start) = 2024
        """
        
        result = db.execute(text(query)).fetchone()
        
        print('=== RELATÓRIO DE CUSTOS 2024 ===')
        print(f'Total de registros: {result.total_records:,}')
        print(f'Custo total 2024: ${result.total_cost_2024:,.2f}')
        print(f'Custo médio por registro: ${result.average_cost:.2f}')
        print(f'Menor custo: ${result.min_cost:.2f}')
        print(f'Maior custo: ${result.max_cost:.2f}')
        print(f'Primeira data: {result.first_date}')
        print(f'Última data: {result.last_date}')
        
        print('\n=== QUERY SQL PARA USAR DIRETAMENTE ===')
        print(query.strip())
        
        # Breakdown por mês
        monthly_query = """
        SELECT 
            EXTRACT(MONTH FROM billing_period_start) as month,
            COUNT(*) as records,
            SUM(effective_cost) as monthly_total
        FROM focus_cost_data 
        WHERE EXTRACT(YEAR FROM billing_period_start) = 2024
        GROUP BY EXTRACT(MONTH FROM billing_period_start)
        ORDER BY month
        """
        
        monthly_results = db.execute(text(monthly_query)).fetchall()
        
        print('\n=== BREAKDOWN MENSAL 2024 ===')
        for row in monthly_results:
            month_name = ["", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", 
                         "Jul", "Ago", "Set", "Out", "Nov", "Dez"][int(row.month)]
            print(f'{month_name}: {row.records} registros, ${row.monthly_total:,.2f}')
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
