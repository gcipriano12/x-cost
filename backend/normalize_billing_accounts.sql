-- Script para normalizar billing_account_id para ter apenas 2 por provider
-- Cada provider terá apenas 2 accounts: Production e Development

BEGIN;

-- Primeiro, vamos ver o que temos atualmente
SELECT 
    provider_name,
    COUNT(DISTINCT billing_account_id) as distinct_accounts
FROM finops.focus_cost_data
GROUP BY provider_name
ORDER BY provider_name;

-- Atualizar AWS accounts
-- Dividir em 2 groups: metade vai para Production, metade para Development
WITH aws_accounts AS (
    SELECT DISTINCT billing_account_id,
           ROW_NUMBER() OVER (ORDER BY billing_account_id) as rn,
           COUNT(*) OVER () as total_accounts
    FROM finops.focus_cost_data 
    WHERE provider_name = 'AWS' 
      AND billing_account_id IS NOT NULL
),
aws_mapping AS (
    SELECT billing_account_id,
           CASE 
               WHEN rn <= (total_accounts / 2) THEN '123456789012'
               ELSE '123456789013'
           END as new_account_id,
           CASE 
               WHEN rn <= (total_accounts / 2) THEN 'AWS Production Account'
               ELSE 'AWS Development Account'
           END as new_account_name
    FROM aws_accounts
)
UPDATE finops.focus_cost_data 
SET billing_account_id = aws_mapping.new_account_id,
    billing_account_name = aws_mapping.new_account_name
FROM aws_mapping
WHERE finops.focus_cost_data.provider_name = 'AWS' 
  AND finops.focus_cost_data.billing_account_id = aws_mapping.billing_account_id;

-- Atualizar Azure accounts
WITH azure_accounts AS (
    SELECT DISTINCT billing_account_id,
           ROW_NUMBER() OVER (ORDER BY billing_account_id) as rn,
           COUNT(*) OVER () as total_accounts
    FROM finops.focus_cost_data 
    WHERE provider_name = 'Azure' 
      AND billing_account_id IS NOT NULL
),
azure_mapping AS (
    SELECT billing_account_id,
           CASE 
               WHEN rn <= (total_accounts / 2) THEN 'sub-12345678-1234-1234-1234-123456789012'
               ELSE 'sub-87654321-4321-4321-4321-210987654321'
           END as new_account_id,
           CASE 
               WHEN rn <= (total_accounts / 2) THEN 'Azure Production Subscription'
               ELSE 'Azure Development Subscription'
           END as new_account_name
    FROM azure_accounts
)
UPDATE finops.focus_cost_data 
SET billing_account_id = azure_mapping.new_account_id,
    billing_account_name = azure_mapping.new_account_name
FROM azure_mapping
WHERE finops.focus_cost_data.provider_name = 'Azure' 
  AND finops.focus_cost_data.billing_account_id = azure_mapping.billing_account_id;

-- Atualizar GCP accounts
WITH gcp_accounts AS (
    SELECT DISTINCT billing_account_id,
           ROW_NUMBER() OVER (ORDER BY billing_account_id) as rn,
           COUNT(*) OVER () as total_accounts
    FROM finops.focus_cost_data 
    WHERE provider_name = 'GCP' 
      AND billing_account_id IS NOT NULL
),
gcp_mapping AS (
    SELECT billing_account_id,
           CASE 
               WHEN rn <= (total_accounts / 2) THEN '012345-ABCDEF-678901'
               ELSE '567890-FEDCBA-123456'
           END as new_account_id,
           CASE 
               WHEN rn <= (total_accounts / 2) THEN 'GCP Production Project'
               ELSE 'GCP Development Project'
           END as new_account_name
    FROM gcp_accounts
)
UPDATE finops.focus_cost_data 
SET billing_account_id = gcp_mapping.new_account_id,
    billing_account_name = gcp_mapping.new_account_name
FROM gcp_mapping
WHERE finops.focus_cost_data.provider_name = 'GCP' 
  AND finops.focus_cost_data.billing_account_id = gcp_mapping.billing_account_id;

-- Atualizar Oracle accounts
WITH oracle_accounts AS (
    SELECT DISTINCT billing_account_id,
           ROW_NUMBER() OVER (ORDER BY billing_account_id) as rn,
           COUNT(*) OVER () as total_accounts
    FROM finops.focus_cost_data 
    WHERE provider_name = 'Oracle' 
      AND billing_account_id IS NOT NULL
),
oracle_mapping AS (
    SELECT billing_account_id,
           CASE 
               WHEN rn <= (total_accounts / 2) THEN 'ocid1.tenancy.oc1..prod123456789'
               ELSE 'ocid1.tenancy.oc1..dev987654321'
           END as new_account_id,
           CASE 
               WHEN rn <= (total_accounts / 2) THEN 'Oracle Production Tenancy'
               ELSE 'Oracle Development Tenancy'
           END as new_account_name
    FROM oracle_accounts
)
UPDATE finops.focus_cost_data 
SET billing_account_id = oracle_mapping.new_account_id,
    billing_account_name = oracle_mapping.new_account_name
FROM oracle_mapping
WHERE finops.focus_cost_data.provider_name = 'Oracle' 
  AND finops.focus_cost_data.billing_account_id = oracle_mapping.billing_account_id;

-- Tratar registros com billing_account_id NULL
-- AWS NULL records
UPDATE finops.focus_cost_data 
SET billing_account_id = '123456789012',
    billing_account_name = 'AWS Production Account'
WHERE provider_name = 'AWS' 
  AND billing_account_id IS NULL;

-- Azure NULL records  
UPDATE finops.focus_cost_data 
SET billing_account_id = 'sub-12345678-1234-1234-1234-123456789012',
    billing_account_name = 'Azure Production Subscription'
WHERE provider_name = 'Azure' 
  AND billing_account_id IS NULL;

-- GCP NULL records
UPDATE finops.focus_cost_data 
SET billing_account_id = '012345-ABCDEF-678901',
    billing_account_name = 'GCP Production Project'
WHERE provider_name = 'GCP' 
  AND billing_account_id IS NULL;

-- Oracle NULL records
UPDATE finops.focus_cost_data 
SET billing_account_id = 'ocid1.tenancy.oc1..prod123456789',
    billing_account_name = 'Oracle Production Tenancy'
WHERE provider_name = 'Oracle' 
  AND billing_account_id IS NULL;

-- Verificar o resultado
SELECT 
    provider_name,
    billing_account_id,
    billing_account_name,
    COUNT(*) as record_count,
    SUM(effective_cost) as total_cost
FROM finops.focus_cost_data 
GROUP BY provider_name, billing_account_id, billing_account_name
ORDER BY provider_name, billing_account_id;

-- Verificar contagem final
SELECT 
    provider_name,
    COUNT(DISTINCT billing_account_id) as distinct_accounts
FROM finops.focus_cost_data 
GROUP BY provider_name
ORDER BY provider_name;

COMMIT;
