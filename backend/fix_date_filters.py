#!/usr/bin/env python3
"""
Script para corrigir os filtros de data no cost_analytics.py
Trocar billing_period_start/end por charge_period_start para filtros de tempo
"""
import re

# Ler o arquivo
with open('app/cost_analytics.py', 'r') as f:
    content = f.read()

# Padrões de substituição
patterns = [
    # Filtros básicos de data
    (r'FocusCostData\.billing_period_start >= start_date', 'FocusCostData.charge_period_start >= start_date'),
    (r'FocusCostData\.billing_period_end <= end_date', 'FocusCostData.charge_period_start <= end_date'),
    
    # Filtros com AND
    (r'FocusCostData\.billing_period_start >= current_period_start', 'FocusCostData.charge_period_start >= current_period_start'),
    (r'FocusCostData\.billing_period_end <= current_period_end', 'FocusCostData.charge_period_start <= current_period_end'),
    (r'FocusCostData\.billing_period_start >= comparison_period_start', 'FocusCostData.charge_period_start >= comparison_period_start'),
    (r'FocusCostData\.billing_period_end <= comparison_period_end', 'FocusCostData.charge_period_start <= comparison_period_end'),
    (r'FocusCostData\.billing_period_start >= period_start', 'FocusCostData.charge_period_start >= period_start'),
    (r'FocusCostData\.billing_period_end <= period_end', 'FocusCostData.charge_period_start <= period_end'),
]

# Aplicar substituições
original_content = content
for pattern, replacement in patterns:
    content = re.sub(pattern, replacement, content)

# Contar quantas mudanças foram feitas
changes_made = content != original_content
total_changes = sum(len(re.findall(pattern, original_content)) for pattern, _ in patterns)

print(f"Mudanças encontradas: {total_changes}")

if changes_made:
    # Fazer backup
    with open('app/cost_analytics.py.backup', 'w') as f:
        f.write(original_content)
    
    # Salvar arquivo corrigido
    with open('app/cost_analytics.py', 'w') as f:
        f.write(content)
    
    print("✅ Arquivo corrigido! Backup salvo em cost_analytics.py.backup")
else:
    print("❌ Nenhuma mudança foi necessária")
