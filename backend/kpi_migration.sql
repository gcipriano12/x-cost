-- Migração: Sistema de KPIs
-- Data: 2025-01-11
-- Descrição: Criação das tabelas para gerenciamento de KPIs

-- Extensão UUID se não existir
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enum para categorias de KPI
CREATE TYPE kpi_category AS ENUM ('efficiency', 'pricing', 'planning', 'governance');

-- Tabela de definições de KPIs
CREATE TABLE IF NOT EXISTS kpi_definitions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category kpi_category NOT NULL,
    formula TEXT,
    unit VARCHAR(20),
    is_good_when_higher BOOLEAN NOT NULL DEFAULT true,
    is_active BOOLEAN NOT NULL DEFAULT true,
    calculation_method VARCHAR(50) NOT NULL DEFAULT 'simple',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de configurações por empresa
CREATE TABLE IF NOT EXISTS kpi_company_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    kpi_definition_id UUID NOT NULL REFERENCES kpi_definitions(id) ON DELETE CASCADE,
    company_id VARCHAR(100) NOT NULL,
    target_value DECIMAL(15,4),
    warning_threshold DECIMAL(15,4),
    critical_threshold DECIMAL(15,4),
    is_enabled BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(kpi_definition_id, company_id)
);

-- Tabela de resultados de KPIs
CREATE TABLE IF NOT EXISTS kpi_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    kpi_definition_id UUID NOT NULL REFERENCES kpi_definitions(id) ON DELETE CASCADE,
    company_id VARCHAR(100) NOT NULL,
    calculation_date DATE NOT NULL,
    value DECIMAL(15,4) NOT NULL,
    trend DECIMAL(8,4),
    status VARCHAR(20) NOT NULL DEFAULT 'neutral',
    meta_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(kpi_definition_id, company_id, calculation_date)
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_kpi_results_company_date ON kpi_results(company_id, calculation_date DESC);
CREATE INDEX IF NOT EXISTS idx_kpi_results_definition_date ON kpi_results(kpi_definition_id, calculation_date DESC);
CREATE INDEX IF NOT EXISTS idx_kpi_company_configs_company ON kpi_company_configs(company_id);
CREATE INDEX IF NOT EXISTS idx_kpi_definitions_category ON kpi_definitions(category);
CREATE INDEX IF NOT EXISTS idx_kpi_definitions_active ON kpi_definitions(is_active) WHERE is_active = true;

-- Função para atualizar timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para atualizar timestamp
CREATE TRIGGER update_kpi_definitions_updated_at BEFORE UPDATE ON kpi_definitions FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_kpi_company_configs_updated_at BEFORE UPDATE ON kpi_company_configs FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

-- Inserir KPIs básicos
INSERT INTO kpi_definitions (code, name, description, category, formula, unit, is_good_when_higher) VALUES
('resource_utilization_rate', 'Taxa de Utilização de Recursos', 'Mede o percentual de recursos provisionados que estão sendo efetivamente utilizados', 'efficiency', '(Capacidade Consumida ÷ Capacidade Alocada) × 100', '%', true),
('cloud_waste_percentage', 'Percentual de Desperdício na Nuvem', 'Identifica a porção do gasto em recursos ociosos como VMs paradas, volumes não anexados', 'efficiency', '(Custo de Recursos Ociosos ÷ Gasto Total na Nuvem) × 100', '%', false),
('power_schedule_adherence', 'Aderência ao Cronograma de Energia', 'Verifica se a automação de start/stop está funcionando conforme planejado', 'efficiency', '(Horas de Runtime Planejadas ÷ Horas de Runtime Reais) × 100', '%', true),
('legacy_resources_percentage', 'Percentual de Recursos Legacy', 'Quantifica quantas instâncias ainda estão em famílias antigas e menos eficientes', 'efficiency', '(Contagem de Instâncias Legacy ÷ Total de Instâncias) × 100', '%', false),
('effective_savings_rate', 'Taxa de Economia Efetiva', 'Economia líquida comparada com preços on-demand', 'pricing', '(Economias de Todos os Instrumentos de Desconto ÷ Gasto On-Demand Equivalente)', '%', true),
('commitment_discount_waste', 'Desperdício de Desconto por Compromisso', 'Quanto da capacidade de RI/SP/CUD comprada permanece não utilizada', 'pricing', '(Custo de Commitment Não Usado ÷ Custo Total de Commitment) × 100', '%', false),
('compute_covered_by_commitments', 'Compute Coberto por Compromissos', 'Profundidade da cobertura de taxa', 'pricing', '(Gasto de Compute com Desconto de Commitment ÷ Gasto Total de Compute) × 100', '%', true),
('cost_per_vcpu_hour', 'Custo por vCPU por Hora', 'Normaliza o custo para uma unidade técnica', 'pricing', '(Custo de Compute por Hora ÷ Número de vCPUs ou GPUs)', 'R$/vCPU/h', false),
('budget_forecast_variation', 'Variação do Forecast do Orçamento', 'Quão próximo seu forecast contínuo está do orçamento acumulado no ano', 'planning', '((Orçado - Previsto) ÷ Orçado) × 100', '%', false),
('cloud_spend_variation', 'Variação do Gasto na Nuvem', 'O sinal clássico de gasto acima/abaixo do orçamento', 'planning', '((Orçado - Real) ÷ Orçado) × 100', '%', false),
('forecast_accuracy_rate', 'Taxa de Precisão do Forecast', 'Precisão preditiva para capacidade ou valores', 'planning', '100 - abs((Previsto - Real) ÷ Previsto) × 100', '%', true),
('unallocated_cost_percentage', 'Percentual de Custo Não Alocado', 'Quanto do gasto ainda não possui tag ou proprietário', 'governance', '(Custos Não Alocados ÷ Gasto Total na Nuvem) × 100', '%', false),
('tag_compliance_rate', 'Taxa de Compliance de Tags', 'Saúde da sua disciplina de tagging', 'governance', '(Recursos Tagueados Corretamente ÷ Total de Recursos) × 100', '%', true),
('anomaly_detection_savings', 'Economias de Detecção de Anomalias', 'Economias realizadas ao detectar picos de gasto antecipadamente', 'governance', 'Soma de (Custo de Pico Previsto - Custo no Desligamento)', 'R$', true)
ON CONFLICT (code) DO NOTHING;

-- Inserir configurações padrão para empresa 'default'
INSERT INTO kpi_company_configs (kpi_definition_id, company_id, target_value, warning_threshold, critical_threshold)
SELECT 
    id,
    'default',
    CASE 
        WHEN code = 'resource_utilization_rate' THEN 75.0
        WHEN code = 'cloud_waste_percentage' THEN 15.0
        WHEN code = 'power_schedule_adherence' THEN 90.0
        WHEN code = 'legacy_resources_percentage' THEN 20.0
        WHEN code = 'effective_savings_rate' THEN 30.0
        WHEN code = 'commitment_discount_waste' THEN 10.0
        WHEN code = 'compute_covered_by_commitments' THEN 70.0
        WHEN code = 'cost_per_vcpu_hour' THEN 0.15
        WHEN code = 'budget_forecast_variation' THEN 5.0
        WHEN code = 'cloud_spend_variation' THEN 5.0
        WHEN code = 'forecast_accuracy_rate' THEN 85.0
        WHEN code = 'unallocated_cost_percentage' THEN 10.0
        WHEN code = 'tag_compliance_rate' THEN 95.0
        WHEN code = 'anomaly_detection_savings' THEN 1000.0
        ELSE 100.0
    END,
    CASE 
        WHEN code = 'resource_utilization_rate' THEN 60.0
        WHEN code = 'cloud_waste_percentage' THEN 25.0
        WHEN code = 'power_schedule_adherence' THEN 75.0
        WHEN code = 'legacy_resources_percentage' THEN 35.0
        WHEN code = 'effective_savings_rate' THEN 20.0
        WHEN code = 'commitment_discount_waste' THEN 20.0
        WHEN code = 'compute_covered_by_commitments' THEN 50.0
        WHEN code = 'cost_per_vcpu_hour' THEN 0.25
        WHEN code = 'budget_forecast_variation' THEN 10.0
        WHEN code = 'cloud_spend_variation' THEN 10.0
        WHEN code = 'forecast_accuracy_rate' THEN 70.0
        WHEN code = 'unallocated_cost_percentage' THEN 20.0
        WHEN code = 'tag_compliance_rate' THEN 80.0
        WHEN code = 'anomaly_detection_savings' THEN 500.0
        ELSE 75.0
    END,
    CASE 
        WHEN code = 'resource_utilization_rate' THEN 40.0
        WHEN code = 'cloud_waste_percentage' THEN 40.0
        WHEN code = 'power_schedule_adherence' THEN 50.0
        WHEN code = 'legacy_resources_percentage' THEN 50.0
        WHEN code = 'effective_savings_rate' THEN 10.0
        WHEN code = 'commitment_discount_waste' THEN 35.0
        WHEN code = 'compute_covered_by_commitments' THEN 30.0
        WHEN code = 'cost_per_vcpu_hour' THEN 0.40
        WHEN code = 'budget_forecast_variation' THEN 20.0
        WHEN code = 'cloud_spend_variation' THEN 20.0
        WHEN code = 'forecast_accuracy_rate' THEN 50.0
        WHEN code = 'unallocated_cost_percentage' THEN 35.0
        WHEN code = 'tag_compliance_rate' THEN 60.0
        WHEN code = 'anomaly_detection_savings' THEN 100.0
        ELSE 50.0
    END
FROM kpi_definitions
ON CONFLICT (kpi_definition_id, company_id) DO NOTHING;

-- Inserir alguns dados de exemplo para demonstração
INSERT INTO kpi_results (kpi_definition_id, company_id, calculation_date, value, trend, status, meta_data)
SELECT 
    d.id,
    'default',
    CURRENT_DATE - INTERVAL '1 day' * generate_series(0, 7),
    CASE 
        WHEN d.code = 'resource_utilization_rate' THEN 65.0 + random() * 20
        WHEN d.code = 'cloud_waste_percentage' THEN 10.0 + random() * 15
        WHEN d.code = 'tag_compliance_rate' THEN 85.0 + random() * 10
        WHEN d.code = 'effective_savings_rate' THEN 25.0 + random() * 15
        ELSE 50.0 + random() * 30
    END,
    (random() - 0.5) * 10, -- trend entre -5 e +5
    CASE 
        WHEN random() < 0.6 THEN 'good'
        WHEN random() < 0.8 THEN 'warning'
        ELSE 'critical'
    END,
    '{"source": "demo", "calculation_method": "simulated"}'::jsonb
FROM kpi_definitions d
CROSS JOIN generate_series(0, 7)
ON CONFLICT (kpi_definition_id, company_id, calculation_date) DO NOTHING;

-- Comentário de finalização
SELECT 'KPI migration completed successfully' as status;
