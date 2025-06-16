#!/usr/bin/env python3
"""
Script para popular o LocalStack com dados de teste para Cost Explorer e outras APIs AWS
"""

import boto3
import json
import time
from datetime import datetime, timedelta
from botocore.config import Config

# Configuração do LocalStack
LOCALSTACK_ENDPOINT = "http://localhost:4566"
AWS_REGION = "us-east-1"

def create_aws_clients():
    """Cria clientes AWS apontando para LocalStack"""
    
    config = Config(
        region_name=AWS_REGION,
        retries={'max_attempts': 3},
        signature_version='v4'
    )
    
    session = boto3.Session(
        aws_access_key_id='test',
        aws_secret_access_key='test',
        region_name=AWS_REGION
    )
    
    clients = {
        'ce': session.client(
            'ce', 
            endpoint_url=LOCALSTACK_ENDPOINT,
            config=config
        ),
        'compute-optimizer': session.client(
            'compute-optimizer',
            endpoint_url=LOCALSTACK_ENDPOINT,
            config=config
        ),
        'ec2': session.client(
            'ec2',
            endpoint_url=LOCALSTACK_ENDPOINT,
            config=config
        ),
        'elbv2': session.client(
            'elbv2',
            endpoint_url=LOCALSTACK_ENDPOINT,
            config=config
        ),
        'rds': session.client(
            'rds',
            endpoint_url=LOCALSTACK_ENDPOINT,
            config=config
        ),
        'lambda': session.client(
            'lambda',
            endpoint_url=LOCALSTACK_ENDPOINT,
            config=config
        )
    }
    
    return clients

def wait_for_localstack():
    """Aguarda LocalStack estar pronto"""
    import requests
    import time
    
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{LOCALSTACK_ENDPOINT}/_localstack/health")
            if response.status_code == 200:
                print("✅ LocalStack está pronto!")
                return True
        except:
            pass
        
        print(f"⏳ Aguardando LocalStack... ({i+1}/{max_retries})")
        time.sleep(2)
    
    print("❌ LocalStack não respondeu a tempo")
    return False

def create_mock_cost_explorer_data():
    """
    Cria dados mock para Cost Explorer no LocalStack
    Nota: LocalStack pode não suportar todas as APIs do Cost Explorer,
    então vamos criar um mock service interno
    """
    print("📊 Criando dados mock para Cost Explorer...")
    
    # Dados mock que serão retornados pelas APIs
    mock_data = {
        'rightsizing_recommendations': {
            'RightsizingRecommendations': [
                {
                    'AccountId': '123456789012',
                    'EstimatedMonthlySavings': {'Amount': '150.50'},
                    'CurrentInstance': {
                        'InstanceName': 'i-1234567890abcdef0',
                        'InstanceType': 'm5.large',
                        'Region': 'us-east-1',
                        'UtilizationMetrics': [
                            {'Key': 'CPUUtilization', 'Value': '25.5'}
                        ]
                    },
                    'ModifyRecommendationDetail': {
                        'TargetInstances': [
                            {'InstanceType': 'm5.medium'}
                        ]
                    }
                },
                {
                    'AccountId': '123456789012',
                    'EstimatedMonthlySavings': {'Amount': '275.00'},
                    'CurrentInstance': {
                        'InstanceName': 'i-0987654321fedcba0',
                        'InstanceType': 'm5.xlarge',
                        'Region': 'us-west-2'
                    },
                    'ModifyRecommendationDetail': {
                        'TargetInstances': [
                            {'InstanceType': 'm5.large'}
                        ]
                    }
                }
            ]
        },
        'reservation_recommendations': {
            'Recommendations': [
                {
                    'AccountId': '123456789012',
                    'RecommendationDetails': {
                        'EstimatedMonthlySavingsAmount': '450.00',
                        'InstanceDetails': {
                            'EC2InstanceDetails': {
                                'Family': 'm5',
                                'InstanceType': 'm5.large',
                                'Region': 'us-east-1'
                            }
                        }
                    }
                },
                {
                    'AccountId': '123456789012',
                    'RecommendationDetails': {
                        'EstimatedMonthlySavingsAmount': '320.00',
                        'InstanceDetails': {
                            'EC2InstanceDetails': {
                                'Family': 'r5',
                                'InstanceType': 'r5.xlarge',
                                'Region': 'us-west-2'
                            }
                        }
                    }
                }
            ]
        },
        'savings_plans_recommendations': {
            'SavingsPlansRecommendationDetails': [
                {
                    'AccountId': '123456789012',
                    'EstimatedMonthlySavings': 380.00,
                    'HourlyCommitmentToPurchase': 5.25,
                    'EstimatedSavingsPercentage': 18.5
                },
                {
                    'AccountId': '123456789012',
                    'EstimatedMonthlySavings': 220.00,
                    'HourlyCommitmentToPurchase': 3.10,
                    'EstimatedSavingsPercentage': 15.2
                }
            ]
        },
        'anomalies': {
            'Anomalies': [
                {
                    'AnomalyId': 'anom-001',
                    'AnomalyStartDate': '2025-06-15',
                    'AnomalyEndDate': '2025-06-16',
                    'DimensionKey': 'EC2-Instance',
                    'Impact': {
                        'MaxImpact': 125.50,
                        'TotalImpact': 125.50
                    },
                    'RootCauses': [
                        {
                            'Service': 'EC2',
                            'UsageType': 'BoxUsage:m5.large',
                            'Region': 'us-east-1'
                        }
                    ],
                    'MonitorArn': 'arn:aws:ce:us-east-1:123456789012:anomaly-monitor/anom-monitor-001'
                }
            ]
        },
        'ebs_recommendations': {
            'volumeRecommendations': [
                {
                    'volumeArn': 'arn:aws:ec2:us-east-1:123456789012:volume/vol-1234567890abcdef0',
                    'finding': 'Overprovisioned',
                    'currentConfiguration': {
                        'volumeType': 'gp2',
                        'volumeSize': 500
                    }
                },
                {
                    'volumeArn': 'arn:aws:ec2:us-west-2:123456789012:volume/vol-0987654321fedcba0',
                    'finding': 'NotOptimized',
                    'currentConfiguration': {
                        'volumeType': 'io1',
                        'volumeSize': 200
                    }
                }
            ]
        }
    }
    
    # Salvar dados mock em arquivo para o servidor local usar
    with open('/tmp/localstack_mock_data.json', 'w') as f:
        json.dump(mock_data, f, indent=2)
    
    print("✅ Dados mock criados em /tmp/localstack_mock_data.json")
    return mock_data

def create_ec2_resources(ec2_client):
    """Cria recursos EC2 mock"""
    print("🖥️ Criando recursos EC2...")
    
    try:
        # Criar VPC
        vpc_response = ec2_client.create_vpc(CidrBlock='10.0.0.0/16')
        vpc_id = vpc_response['Vpc']['VpcId']
        print(f"   ✅ VPC criada: {vpc_id}")
        
        # Criar subnet
        subnet_response = ec2_client.create_subnet(
            VpcId=vpc_id,
            CidrBlock='10.0.1.0/24'
        )
        subnet_id = subnet_response['Subnet']['SubnetId']
        print(f"   ✅ Subnet criada: {subnet_id}")
        
        # Criar instâncias EC2 (simuladas)
        instances_data = [
            {'type': 'm5.large', 'name': 'test-instance-1'},
            {'type': 'm5.xlarge', 'name': 'test-instance-2'},
            {'type': 'r5.large', 'name': 'test-instance-3'}
        ]
        
        for instance in instances_data:
            try:
                response = ec2_client.run_instances(
                    ImageId='ami-12345678',  # Mock AMI
                    MinCount=1,
                    MaxCount=1,
                    InstanceType=instance['type']
                )
                instance_id = response['Instances'][0]['InstanceId']
                print(f"   ✅ Instância {instance['name']} criada: {instance_id}")
            except Exception as e:
                print(f"   ⚠️ Erro ao criar instância {instance['name']}: {e}")
        
    except Exception as e:
        print(f"   ❌ Erro ao criar recursos EC2: {e}")

def create_load_balancer_resources(elbv2_client, ec2_client):
    """Cria recursos de Load Balancer"""
    print("⚖️ Criando Load Balancers...")
    
    try:
        # Primeiro, listar VPCs disponíveis
        vpcs = ec2_client.describe_vpcs()
        if vpcs['Vpcs']:
            vpc_id = vpcs['Vpcs'][0]['VpcId']
            
            # Listar subnets
            subnets = ec2_client.describe_subnets(
                Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
            )
            
            if subnets['Subnets']:
                subnet_ids = [subnet['SubnetId'] for subnet in subnets['Subnets']]
                
                # Criar Application Load Balancer
                alb_response = elbv2_client.create_load_balancer(
                    Name='test-alb-1',
                    Subnets=subnet_ids[:2] if len(subnet_ids) >= 2 else subnet_ids,
                    SecurityGroups=[],
                    Scheme='internal',
                    Type='application'
                )
                alb_arn = alb_response['LoadBalancers'][0]['LoadBalancerArn']
                print(f"   ✅ ALB criado: {alb_arn}")
                
    except Exception as e:
        print(f"   ❌ Erro ao criar Load Balancers: {e}")

def create_rds_resources(rds_client):
    """Cria recursos RDS"""
    print("🗄️ Criando instâncias RDS...")
    
    try:
        # Criar instância RDS
        rds_response = rds_client.create_db_instance(
            DBInstanceIdentifier='test-db-instance-1',
            DBInstanceClass='db.t3.medium',
            Engine='mysql',
            MasterUsername='admin',
            MasterUserPassword='password123',
            AllocatedStorage=20
        )
        print(f"   ✅ Instância RDS criada: test-db-instance-1")
        
    except Exception as e:
        print(f"   ❌ Erro ao criar instância RDS: {e}")

def create_lambda_resources(lambda_client):
    """Cria funções Lambda"""
    print("λ Criando funções Lambda...")
    
    try:
        # Código básico da função
        lambda_code = """
def lambda_handler(event, context):
    return {'statusCode': 200, 'body': 'Hello from Lambda!'}
        """
        
        # Criar função Lambda
        lambda_response = lambda_client.create_function(
            FunctionName='test-function-1',
            Runtime='python3.9',
            Role='arn:aws:iam::123456789012:role/lambda-role',
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': lambda_code.encode()},
            MemorySize=1024,
            Timeout=300
        )
        print(f"   ✅ Função Lambda criada: test-function-1")
        
    except Exception as e:
        print(f"   ❌ Erro ao criar função Lambda: {e}")

def main():
    """Função principal"""
    print("🚀 Iniciando população do LocalStack com dados de teste...")
    
    # Aguardar LocalStack estar pronto
    if not wait_for_localstack():
        return
    
    # Criar dados mock
    create_mock_cost_explorer_data()
    
    # Criar clientes AWS
    try:
        clients = create_aws_clients()
        print("✅ Clientes AWS criados")
    except Exception as e:
        print(f"❌ Erro ao criar clientes AWS: {e}")
        return
    
    # Criar recursos
    create_ec2_resources(clients['ec2'])
    create_load_balancer_resources(clients['elbv2'], clients['ec2'])
    create_rds_resources(clients['rds'])
    create_lambda_resources(clients['lambda'])
    
    print("🎉 População do LocalStack concluída!")
    print("📋 Dados criados:")
    print("   - Dados mock do Cost Explorer em /tmp/localstack_mock_data.json")
    print("   - Instâncias EC2 simuladas")
    print("   - Load Balancers")
    print("   - Instâncias RDS")
    print("   - Funções Lambda")
    print("")
    print("🔗 Agora você pode testar os endpoints:")
    print("   - http://localhost:8000/api/v1/savings-opportunities")
    print("   - http://localhost:8000/api/v1/anomalies")
    print("   - http://localhost:8000/api/v1/optimization/summary")

if __name__ == "__main__":
    main()
