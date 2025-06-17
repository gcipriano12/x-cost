#!/usr/bin/env python3
"""
Script para popular dados de teste para Savings Opportunities
Gera dados compatíveis com a estrutura esperada pelo frontend
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

def generate_mock_savings_opportunities(count: int = 50) -> List[Dict[str, Any]]:
    """Gera oportunidades de economia mock para teste"""
    
    providers = ['AWS', 'Azure', 'GCP', 'Oracle']
    services = [
        'EC2', 'RDS', 'S3', 'Lambda', 'ELB',
        'Virtual Machines', 'Storage', 'App Service', 'SQL Database',
        'Compute Engine', 'Cloud Storage', 'BigQuery', 'Cloud Functions',
        'Compute', 'Object Storage', 'Database', 'Load Balancer'
    ]
    
    categories = [
        'rightsizing', 'unused_resources', 'reserved_instances', 
        'spot_instances', 'storage_optimization', 'network_optimization',
        'idle_resources', 'scheduling'
    ]
    
    confidence_levels = ['high', 'medium', 'low']
    effort_levels = ['low', 'medium', 'high']
    risk_levels = ['low', 'medium', 'high']
    
    regions = [
        'us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1',
        'East US', 'West Europe', 'Southeast Asia', 'Central US',
        'us-central1', 'europe-west1', 'asia-southeast1'
    ]
    
    opportunities = []
    
    for i in range(count):
        provider = random.choice(providers)
        service = random.choice(services)
        category = random.choice(categories)
        confidence_level = random.choice(confidence_levels)
        effort_level = random.choice(effort_levels)
        risk_level = random.choice(risk_levels)
        
        # Generate savings amounts
        monthly_savings = round(random.uniform(50, 10000), 2)
        annual_savings = monthly_savings * 12
        
        # Generate confidence numeric value
        confidence_map = {'high': random.uniform(80, 95), 'medium': random.uniform(50, 79), 'low': random.uniform(20, 49)}
        confidence = round(confidence_map[confidence_level], 1)
        
        # Generate effort hours
        effort_hours_map = {'low': random.uniform(1, 8), 'medium': random.uniform(8, 40), 'high': random.uniform(40, 200)}
        effort_hours = round(effort_hours_map[effort_level], 1)
        
        # Generate resource names
        resource_count = random.randint(1, 5)
        affected_resources = [f"{service.lower()}-resource-{j:03d}" for j in range(resource_count)]
        resource_name = affected_resources[0] if affected_resources else f"{service.lower()}-main-resource"
        
        # Generate titles and descriptions based on category
        titles = {
            'rightsizing': f"Rightsize {service} instances in {random.choice(regions)}",
            'unused_resources': f"Remove unused {service} resources",
            'reserved_instances': f"Purchase Reserved Instances for {service}",
            'spot_instances': f"Migrate {service} to Spot Instances",
            'storage_optimization': f"Optimize {service} storage configuration",
            'network_optimization': f"Optimize {service} network usage",
            'idle_resources': f"Address idle {service} resources",
            'scheduling': f"Implement scheduled scaling for {service}"
        }
        
        descriptions = {
            'rightsizing': f"Current {service} instances are over-provisioned. Analysis shows CPU utilization averaging {random.randint(10, 40)}% over the last 30 days.",
            'unused_resources': f"Identified {service} resources that have been idle for more than {random.randint(7, 30)} days with no active connections or usage.",
            'reserved_instances': f"High usage pattern detected for {service}. Reserved Instance commitment would reduce costs by {random.randint(20, 40)}%.",
            'spot_instances': f"Workload analysis shows {service} is suitable for Spot Instance usage with fault-tolerant architecture.",
            'storage_optimization': f"Storage analysis reveals {random.randint(20, 60)}% of {service} storage is infrequently accessed and can be moved to cheaper tiers.",
            'network_optimization': f"Network traffic analysis shows opportunities to reduce {service} data transfer costs through regional optimization.",
            'idle_resources': f"{service} resources showing minimal utilization (<{random.randint(5, 15)}%) over extended period.",
            'scheduling': f"Usage patterns for {service} show predictable low-usage periods suitable for automated scaling."
        }
        
        actions = {
            'rightsizing': f"Resize instances from current configuration to recommended smaller instance types",
            'unused_resources': f"Terminate or archive unused {service} resources after stakeholder confirmation",
            'reserved_instances': f"Purchase 1-year Reserved Instances for consistent {service} usage",
            'spot_instances': f"Migrate compatible {service} workloads to Spot Instance pools",
            'storage_optimization': f"Implement intelligent tiering and lifecycle policies for {service} storage",
            'network_optimization': f"Optimize {service} placement and configure regional data transfer policies",
            'idle_resources': f"Schedule automatic shutdown during low-usage periods or migrate to on-demand model",
            'scheduling': f"Configure auto-scaling policies and scheduled actions for {service}"
        }
        
        detected_at = datetime.utcnow() - timedelta(days=random.randint(1, 30))
        
        opportunity = {
            "id": f"opp_{i+1:03d}",
            "provider": provider,
            "service": service,
            "region": random.choice(regions),
            "opportunity_type": category,
            "title": titles[category],
            "description": descriptions[category],
            "category": category,
            "monthly_savings": monthly_savings,
            "estimated_savings": monthly_savings,  # Legacy compatibility
            "annual_savings": annual_savings,
            "potential_savings": monthly_savings,  # Internal field
            "currency": "USD",
            "confidence_level": confidence_level,
            "confidence": confidence,
            "implementation_effort": effort_level,
            "implementation_effort_hours": effort_hours,
            "risk_level": risk_level,
            "affected_resources": affected_resources,
            "resources_affected": affected_resources,  # Legacy compatibility
            "resource_name": resource_name,
            "action_required": actions[category],
            "detected_at": detected_at.isoformat(),
            "created_at": detected_at.isoformat()
        }
        
        opportunities.append(opportunity)
    
    return opportunities

def generate_mock_anomalies(count: int = 30) -> List[Dict[str, Any]]:
    """Gera anomalias mock para teste"""
    
    providers = ['AWS', 'Azure', 'GCP', 'Oracle']
    services = [
        'EC2', 'RDS', 'S3', 'Lambda', 'ELB',
        'Virtual Machines', 'Storage', 'App Service', 'SQL Database',
        'Compute Engine', 'Cloud Storage', 'BigQuery', 'Cloud Functions'
    ]
    
    anomaly_types = ['spike', 'drift', 'unusual_pattern', 'cost_increase']
    severity_levels = ['low', 'medium', 'high', 'critical']
    
    anomalies = []
    
    for i in range(count):
        provider = random.choice(providers)
        service = random.choice(services)
        anomaly_type = random.choice(anomaly_types)
        severity = random.choice(severity_levels)
        
        cost_impact = round(random.uniform(100, 5000), 2)
        
        resource_count = random.randint(1, 3)
        affected_resources = [f"{service.lower()}-{j:03d}" for j in range(resource_count)]
        
        descriptions = {
            'spike': f"Sudden cost spike detected in {service} - {random.randint(200, 800)}% increase over baseline",
            'drift': f"Gradual cost increase in {service} - {random.randint(10, 50)}% above normal trend",
            'unusual_pattern': f"Unusual usage pattern detected in {service} during off-hours",
            'cost_increase': f"Significant cost increase in {service} - {random.randint(30, 150)}% higher than last month"
        }
        
        root_causes = {
            'spike': f"Possible auto-scaling event or new workload deployment",
            'drift': f"Gradual increase in usage or inefficient resource allocation",
            'unusual_pattern': f"After-hours activity or batch processing changes",
            'cost_increase': f"Resource configuration changes or pricing updates"
        }
        
        detected_at = datetime.utcnow() - timedelta(days=random.randint(1, 14))
        
        anomaly = {
            "id": f"anom_{i+1:03d}",
            "provider": provider,
            "service": service,
            "region": random.choice(['us-east-1', 'us-west-2', 'eu-west-1']),
            "anomaly_type": anomaly_type,
            "severity": severity,
            "detected_at": detected_at.isoformat(),
            "cost_impact": cost_impact,
            "currency": "USD",
            "description": descriptions[anomaly_type],
            "root_cause": root_causes[anomaly_type],
            "affected_resources": affected_resources
        }
        
        anomalies.append(anomaly)
    
    return anomalies

def save_test_data():
    """Salva os dados de teste em arquivos JSON"""
    
    print("🔄 Generating mock data...")
    
    # Generate opportunities
    opportunities = generate_mock_savings_opportunities(50)
    with open('/Users/gcipriano/Repositories/x-cost/backend/mock_savings_opportunities.json', 'w') as f:
        json.dump(opportunities, f, indent=2)
    
    # Generate anomalies
    anomalies = generate_mock_anomalies(30)
    with open('/Users/gcipriano/Repositories/x-cost/backend/mock_anomalies.json', 'w') as f:
        json.dump(anomalies, f, indent=2)
    
    # Generate summary statistics
    total_monthly = sum(opp['monthly_savings'] for opp in opportunities)
    total_annual = total_monthly * 12
    
    confidence_counts = {}
    effort_counts = {}
    risk_counts = {}
    category_counts = {}
    
    for opp in opportunities:
        confidence_counts[opp['confidence_level']] = confidence_counts.get(opp['confidence_level'], 0) + 1
        effort_counts[opp['implementation_effort']] = effort_counts.get(opp['implementation_effort'], 0) + 1
        risk_counts[opp['risk_level']] = risk_counts.get(opp['risk_level'], 0) + 1
        category_counts[opp['category']] = category_counts.get(opp['category'], 0) + 1
    
    summary = {
        "total_opportunities": len(opportunities),
        "total_anomalies": len(anomalies),
        "total_monthly_savings": round(total_monthly, 2),
        "total_annual_savings": round(total_annual, 2),
        "confidence_breakdown": confidence_counts,
        "effort_breakdown": effort_counts,
        "risk_breakdown": risk_counts,
        "category_breakdown": category_counts,
        "generated_at": datetime.utcnow().isoformat()
    }
    
    with open('/Users/gcipriano/Repositories/x-cost/backend/mock_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("✅ Mock data generated successfully!")
    print(f"📊 Generated {len(opportunities)} opportunities and {len(anomalies)} anomalies")
    print(f"💰 Total potential savings: ${total_monthly:,.2f}/month (${total_annual:,.2f}/year)")
    print(f"📁 Files saved:")
    print(f"   - mock_savings_opportunities.json")
    print(f"   - mock_anomalies.json") 
    print(f"   - mock_summary.json")

if __name__ == "__main__":
    save_test_data()
