-- Migration: Add KPI Tables
-- Description: Creates tables for Key Performance Indicators system
-- Date: 2025-01-15

-- Create schema if not exists
CREATE SCHEMA IF NOT EXISTS finops;

-- Tabela principal de definições de KPIs
CREATE TABLE finops.kpi_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(20) NOT NULL CHECK (category IN ('efficiency', 'pricing', 'planning', 'governance')),
    description TEXT,
    formula TEXT,
    unit VARCHAR(20),
    target_value DECIMAL(15,4),
    is_good_when_higher BOOLEAN DEFAULT true,
    calculation_frequency VARCHAR(20) DEFAULT 'daily',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de resultados calculados
CREATE TABLE finops.kpi_results (
    id BIGSERIAL PRIMARY KEY,
    kpi_id UUID REFERENCES finops.kpi_definitions(id) ON DELETE CASCADE,
    calculation_date DATE NOT NULL,
    value DECIMAL(15,4) NOT NULL,
    trend DECIMAL(5,2), -- Percentual de mudança
    metadata JSONB, -- Dados adicionais do cálculo
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(kpi_id, calculation_date)
);

-- Tabela de configurações por empresa
CREATE TABLE finops.kpi_company_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kpi_id UUID REFERENCES finops.kpi_definitions(id) ON DELETE CASCADE,
    company_id UUID NOT NULL, -- Referência futura para multi-tenant
    target_value DECIMAL(15,4),
    warning_threshold DECIMAL(15,4),
    critical_threshold DECIMAL(15,4),
    is_enabled BOOLEAN DEFAULT true,
    notification_settings JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(kpi_id, company_id)
);

-- Índices para performance
CREATE INDEX idx_kpi_definitions_code ON finops.kpi_definitions(code);
CREATE INDEX idx_kpi_definitions_category ON finops.kpi_definitions(category);
CREATE INDEX idx_kpi_definitions_active ON finops.kpi_definitions(is_active);
CREATE INDEX idx_kpi_results_date ON finops.kpi_results(calculation_date DESC);
CREATE INDEX idx_kpi_results_kpi_date ON finops.kpi_results(kpi_id, calculation_date DESC);
CREATE INDEX idx_kpi_configs_company ON finops.kpi_company_configs(company_id);

-- Inserir definições padrão de KPIs
INSERT INTO finops.kpi_definitions (code, name, category, description, formula, unit, target_value, is_good_when_higher) VALUES
-- Efficiency
('resource_utilization_rate', 'Resource Utilization Rate', 'efficiency', 
 'Percentual de recursos provisionados que estão sendo efetivamente utilizados', 
 '(consumed_capacity / allocated_capacity) * 100', '%', 75, true),

('cloud_waste_percentage', 'Cloud Waste Percentage', 'efficiency',
 'Percentual do gasto em recursos ociosos ou subutilizados',
 '(idle_resource_cost / total_cloud_spend) * 100', '%', 15, false),

('power_schedule_adherence', 'Power Schedule Adherence Rate', 'efficiency',
 'Aderência ao agendamento de liga/desliga de recursos não-produtivos',
 '(scheduled_hours / total_hours) * 100', '%', 95, true),

('legacy_resources_percentage', 'Legacy Resources Percentage', 'efficiency',
 'Percentual de recursos em gerações antigas menos eficientes',
 '(legacy_instance_count / total_instances) * 100', '%', 20, false),

-- Pricing
('effective_savings_rate', 'Effective Savings Rate (ESR)', 'pricing',
 'Taxa de economia real comparada com preços on-demand',
 '(total_savings / on_demand_equivalent) * 100', '%', 30, true),

('commitment_discount_waste', 'Commitment Discount Waste', 'pricing',
 'Percentual de commitments não utilizados',
 '(unused_commitment_cost / total_commitment_cost) * 100', '%', 10, false),

('compute_covered_by_commitments', 'Compute Covered by Commitments', 'pricing',
 'Cobertura de instâncias por reservas ou savings plans',
 '(committed_compute_cost / total_compute_cost) * 100', '%', 80, true),

('cost_per_vcpu_hour', 'Cost per vCPU/GPU Hour', 'pricing',
 'Custo normalizado por unidade de computação',
 'total_compute_cost / total_vcpu_hours', '$/h', 0.35, false),

-- Planning
('budget_forecast_variation', 'Budget vs. Forecast Variation', 'planning',
 'Variação entre orçamento e previsão',
 'ABS((budget - forecast) / budget) * 100', '%', 5, false),

('cloud_spend_variation', 'Cloud Spend Variation', 'planning',
 'Variação do gasto real vs orçado',
 '((actual - budget) / budget) * 100', '%', 7, false),

('forecast_accuracy_rate', 'Forecast Accuracy Rate', 'planning',
 'Precisão das previsões de custo',
 '(1 - ABS(forecast - actual) / actual) * 100', '%', 90, true),

-- Governance
('unallocated_cost_percentage', 'Unallocated Cost Percentage', 'governance',
 'Percentual de custos sem alocação ou tags',
 '(untagged_cost / total_cost) * 100', '%', 5, false),

('tag_compliance_rate', 'Tag Policy Compliance Rate', 'governance',
 'Aderência às políticas de tagging',
 '(compliant_resources / total_resources) * 100', '%', 95, true),

('anomaly_detection_savings', 'Anomaly Detection Savings', 'governance',
 'Economias realizadas através de detecção de anomalias',
 'SUM(anomaly_prevented_cost)', '$', 50000, true);

-- Comments
COMMENT ON TABLE finops.kpi_definitions IS 'Definições dos KPIs disponíveis no sistema';
COMMENT ON TABLE finops.kpi_results IS 'Resultados históricos dos cálculos de KPIs';
COMMENT ON TABLE finops.kpi_company_configs IS 'Configurações específicas de KPIs por empresa';
