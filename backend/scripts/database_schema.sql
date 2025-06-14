-- PostgreSQL Schema para FinOps FOCUS
-- Criação das tabelas baseadas na especificação FOCUS

-- Schema principal
CREATE SCHEMA IF NOT EXISTS finops;

-- Tabela de provedores de nuvem
CREATE TABLE finops.cloud_providers (
    id SERIAL PRIMARY KEY,
    provider_name VARCHAR(50) NOT NULL UNIQUE,
    api_endpoint VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserir provedores padrão
INSERT INTO finops.cloud_providers (provider_name) VALUES 
('AWS'), ('Azure'), ('GCP'), ('Oracle Cloud');

-- Tabela principal de custos (FOCUS compliant)
CREATE TABLE finops.focus_cost_data (
    id BIGSERIAL PRIMARY KEY,
    
    -- FOCUS Core Dimensions
    billing_account_id VARCHAR(255),
    billing_account_name VARCHAR(255),
    billing_currency VARCHAR(3),
    billing_period_start DATE,
    billing_period_end DATE,
    charge_category VARCHAR(50), -- Usage, Purchase, Tax, Credit, Adjustment
    charge_description TEXT,
    charge_frequency VARCHAR(20), -- One-Time, Recurring, Usage-Based
    charge_period_start TIMESTAMP,
    charge_period_end TIMESTAMP,
    
    -- Cost and Usage
    billed_cost DECIMAL(15,4),
    effective_cost DECIMAL(15,4),
    list_cost DECIMAL(15,4),
    list_unit_price DECIMAL(15,4),
    pricing_category VARCHAR(50), -- On-Demand, Reserved, Spot
    pricing_quantity DECIMAL(15,6),
    pricing_unit VARCHAR(50),
    usage_quantity DECIMAL(15,6),
    usage_unit VARCHAR(50),
    
    -- Provider Information
    provider_name VARCHAR(50) REFERENCES finops.cloud_providers(provider_name),
    publisher_name VARCHAR(100),
    service_category VARCHAR(100),
    service_name VARCHAR(100),
    
    -- Resource Information
    resource_id VARCHAR(255),
    resource_name VARCHAR(255),
    resource_type VARCHAR(100),
    availability_zone VARCHAR(50),
    region VARCHAR(50),
    
    -- Invoice Information
    invoice_issuer_name VARCHAR(100),
    
    -- Metadata
    tags JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_source VARCHAR(50), -- CUR, Cost Management, etc.
    
    -- Índices
    INDEX idx_billing_period (billing_period_start, billing_period_end),
    INDEX idx_provider_service (provider_name, service_name),
    INDEX idx_resource (resource_id, resource_type),
    INDEX idx_cost_date (charge_period_start, charge_period_end),
    INDEX idx_tags_gin (tags) USING GIN
);

-- Particionamento por mês para melhor performance
SELECT partman.create_parent(
    p_parent_table => 'finops.focus_cost_data',
    p_control => 'billing_period_start',
    p_type => 'range',
    p_interval => 'monthly'
);

-- Tabela de análises agregadas
CREATE TABLE finops.cost_analysis (
    id BIGSERIAL PRIMARY KEY,
    analysis_type VARCHAR(50), -- trend, delta, forecast
    provider_name VARCHAR(50),
    service_name VARCHAR(100),
    resource_type VARCHAR(100),
    period_start DATE,
    period_end DATE,
    
    -- Métricas calculadas
    total_cost DECIMAL(15,4),
    average_daily_cost DECIMAL(15,4),
    cost_trend DECIMAL(5,2), -- Percentual de variação
    cost_delta DECIMAL(15,4),
    forecasted_cost DECIMAL(15,4),
    
    -- Metadados da análise
    calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags JSONB,
    
    UNIQUE(analysis_type, provider_name, service_name, period_start, period_end)
);

-- Tabela de orçamentos e alertas
CREATE TABLE finops.budgets (
    id SERIAL PRIMARY KEY,
    budget_name VARCHAR(100) NOT NULL,
    provider_name VARCHAR(50),
    service_name VARCHAR(100),
    budget_amount DECIMAL(15,4),
    budget_period VARCHAR(20), -- monthly, quarterly, yearly
    alert_threshold DECIMAL(5,2), -- Percentual para alerta
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags JSONB
);

-- Tabela de cache para consultas frequentes
CREATE TABLE finops.query_cache (
    cache_key VARCHAR(255) PRIMARY KEY,
    query_result JSONB,
    expiry_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Views para consultas otimizadas
CREATE OR REPLACE VIEW finops.monthly_cost_summary AS
SELECT 
    provider_name,
    service_name,
    DATE_TRUNC('month', billing_period_start) as month,
    SUM(effective_cost) as total_cost,
    AVG(effective_cost) as avg_cost,
    COUNT(*) as record_count
FROM finops.focus_cost_data
GROUP BY provider_name, service_name, DATE_TRUNC('month', billing_period_start);

CREATE OR REPLACE VIEW finops.daily_cost_trend AS
SELECT 
    provider_name,
    DATE(charge_period_start) as cost_date,
    SUM(effective_cost) as daily_cost,
    LAG(SUM(effective_cost)) OVER (PARTITION BY provider_name ORDER BY DATE(charge_period_start)) as previous_day_cost
FROM finops.focus_cost_data
GROUP BY provider_name, DATE(charge_period_start);

-- Função para limpeza de dados antigos
CREATE OR REPLACE FUNCTION finops.cleanup_old_data(months_to_keep INTEGER DEFAULT 24)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM finops.focus_cost_data 
    WHERE billing_period_start < CURRENT_DATE - INTERVAL '1 month' * months_to_keep;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Função para atualizar análises
CREATE OR REPLACE FUNCTION finops.update_cost_analysis()
RETURNS VOID AS $$
BEGIN
    -- Limpar análises antigas
    DELETE FROM finops.cost_analysis WHERE calculation_date < CURRENT_DATE - INTERVAL '7 days';
    
    -- Inserir novas análises de tendência
    INSERT INTO finops.cost_analysis (
        analysis_type, provider_name, service_name, 
        period_start, period_end, total_cost, cost_trend
    )
    SELECT 
        'trend',
        provider_name,
        service_name,
        DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month'),
        DATE_TRUNC('month', CURRENT_DATE),
        SUM(effective_cost),
        CASE 
            WHEN LAG(SUM(effective_cost)) OVER (PARTITION BY provider_name, service_name ORDER BY DATE_TRUNC('month', billing_period_start)) > 0
            THEN ((SUM(effective_cost) - LAG(SUM(effective_cost)) OVER (PARTITION BY provider_name, service_name ORDER BY DATE_TRUNC('month', billing_period_start))) 
                  / LAG(SUM(effective_cost)) OVER (PARTITION BY provider_name, service_name ORDER BY DATE_TRUNC('month', billing_period_start))) * 100
            ELSE 0
        END
    FROM finops.focus_cost_data
    WHERE billing_period_start >= CURRENT_DATE - INTERVAL '2 months'
    GROUP BY provider_name, service_name, DATE_TRUNC('month', billing_period_start)
    ON CONFLICT (analysis_type, provider_name, service_name, period_start, period_end) 
    DO UPDATE SET 
        total_cost = EXCLUDED.total_cost,
        cost_trend = EXCLUDED.cost_trend,
        calculation_date = CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar timestamp
CREATE OR REPLACE FUNCTION finops.update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_focus_cost_data_modtime 
    BEFORE UPDATE ON finops.focus_cost_data 
    FOR EACH ROW EXECUTE FUNCTION finops.update_modified_column();

-- Índices adicionais para performance
CREATE INDEX CONCURRENTLY idx_focus_cost_provider_date 
    ON finops.focus_cost_data (provider_name, billing_period_start DESC);

CREATE INDEX CONCURRENTLY idx_focus_cost_service_cost 
    ON finops.focus_cost_data (service_name, effective_cost DESC);

CREATE INDEX CONCURRENTLY idx_focus_cost_resource_date 
    ON finops.focus_cost_data (resource_id, charge_period_start DESC);

-- Estatísticas para otimização de consultas
ANALYZE finops.focus_cost_data;
ANALYZE finops.cost_analysis;