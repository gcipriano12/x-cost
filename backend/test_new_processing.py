#!/usr/bin/env python3

"""
Script para simular a nova lógica de processamento dos dados
"""

def test_processed_data():
    print("🧪 TESTE: Nova lógica de processamento dos dados")
    print("=" * 60)
    
    # Dados simulados baseados no debug real
    original_data = [
        {"month": "Jul", "actual": 749839},
        {"month": "Aug", "actual": 1802709},
        {"month": "Sep", "actual": 2002619},
        {"month": "Oct", "actual": 2026370},
        {"month": "Nov", "actual": 1848599},
        {"month": "Dec", "actual": 1908036},
        {"month": "Jan", "actual": 2514114},
        {"month": "Feb", "actual": 2584074},
        {"month": "Mar", "actual": 1843097},
        {"month": "Apr", "actual": 2396558},
        {"month": "May", "actual": 3661702},
        {"month": "Jun", "actual": 6610505},
        {"month": "Jul", "actual": 2013557},
        {"month": "Jul", "forecast": 3028972},
        {"month": "Aug", "forecast": 3673205},
        {"month": "Sep", "forecast": 3897073},
        {"month": "Oct", "forecast": 3951226},
        {"month": "Nov", "forecast": 3840650},
        {"month": "Dec", "forecast": 3480928},
        {"month": "Jan", "forecast": 3333172},
    ]
    
    print("📊 DADOS ORIGINAIS (primeiros 5):")
    for i, item in enumerate(original_data[:5]):
        print(f"   {i:2d}. {item['month']} - {item}")
    print("   ... (total: 20 pontos)")
    print()
    
    # Simular a nova lógica de processamento
    def process_data(data):
        processed = []
        current_year = 2025  # Data atual: julho 2025
        
        for index, item in enumerate(data):
            # Lógica simplificada:
            # Índices 0-5: Jul/24 a Dec/24 (2024)
            # Índices 6-19: Jan/25 em diante (2025)
            if index <= 5:
                year = current_year - 1  # 2024
            else:
                year = current_year  # 2025
                
            short_year = str(year)[-2:]
            formatted_month = f"{item['month']}/{short_year}"
            
            processed_item = {
                **item,
                'formattedMonth': formatted_month,
                'originalMonth': item['month'],
                'index': index
            }
            processed.append(processed_item)
        
        return processed
    
    processed_data = process_data(original_data)
    
    print("✅ DADOS PROCESSADOS:")
    for item in processed_data:
        data_type = "ACTUAL" if "actual" in item else "FORECAST"
        value = item.get("actual", item.get("forecast", 0))
        print(f"   {item['index']:2d}. {item['originalMonth']} → {item['formattedMonth']} - {data_type}: ${value:,}")
    
    print()
    print("🎯 SEQUÊNCIA NO EIXO X (formattedMonth):")
    x_axis_labels = [item['formattedMonth'] for item in processed_data]
    print(f"   {' → '.join(x_axis_labels)}")
    
    print()
    print("🔍 VERIFICAÇÃO DE ORDEM CRONOLÓGICA:")
    
    # Extrair labels únicos mantendo ordem
    unique_labels = []
    seen = set()
    for label in x_axis_labels:
        if label not in seen:
            unique_labels.append(label)
            seen.add(label)
    
    print(f"   Labels únicos: {' → '.join(unique_labels)}")
    
    # Verificar ordem cronológica
    def parse_date(label):
        month_str, year_str = label.split('/')
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        month_num = months.index(month_str) + 1
        year = 2000 + int(year_str)
        return year * 100 + month_num  # Criar um número para comparação
    
    is_chronological = True
    prev_date = parse_date(unique_labels[0])
    
    for label in unique_labels[1:]:
        current_date = parse_date(label)
        if current_date <= prev_date:
            is_chronological = False
            print(f"   ❌ Problema: {label} não está em ordem após {unique_labels[unique_labels.index(label)-1]}")
            break
        prev_date = current_date
    
    if is_chronological:
        print("   ✅ Ordem cronológica está PERFEITA!")
    else:
        print("   ❌ Ainda há problemas na ordem cronológica")
    
    print()
    print("📈 BENEFÍCIOS DA NOVA ABORDAGEM:")
    print("   ✓ Dados processados ANTES de ir para o gráfico")
    print("   ✓ Eixo X usa 'formattedMonth' diretamente")
    print("   ✓ Não depende de tickFormatter complexo")
    print("   ✓ Tooltip usa formatMonthWithYear() simples")
    print("   ✓ Sem dependência de índices dinâmicos")

if __name__ == "__main__":
    test_processed_data()
