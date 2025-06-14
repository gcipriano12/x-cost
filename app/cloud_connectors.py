import boto3
import pandas as pd
from azure.identity import DefaultAzureCredential
from azure.mgmt.consumption import ConsumptionManagementClient
from google.cloud import billing
import oci
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import logging
from decimal import Decimal
from app.models import FocusCostDataCreate

logger = logging.getLogger(__name__)

class CloudConnectorBase:
    """Classe base para conectores de nuvem"""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
    
    def extract_cost_data(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Extrai dados de custo do provedor"""
        raise NotImplementedError("Subclasses must implement extract_cost_data")
    
    def transform_to_focus(self, raw_data: List[Dict[str, Any]]) -> List[FocusCostDataCreate]:
        """Transforma dados brutos para o formato FOCUS"""
        raise NotImplementedError("Subclasses must implement transform_to_focus")

class AWSConnector(CloudConnectorBase):
    """Conector para AWS Cost Explorer e Cost and Usage Reports"""
    
    def __init__(self):
        super().__init__("AWS")
        self.ce_client = boto3.client('ce')
        self.s3_client = boto3.client('s3')
    
    def extract_cost_data(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Extrai dados de custo da AWS via Cost Explorer"""
        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['BlendedCost', 'UsageQuantity'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                    {'Type': 'DIMENSION', 'Key': 'REGION'},
                    {'Type': 'DIMENSION', 'Key': 'USAGE_TYPE'}
                ]
            )
            
            cost_data = []
            for result in response['ResultsByTime']:
                date = datetime.strptime(result['TimePeriod']['Start'], '%Y-%m-%d').date()
                
                for group in result['Groups']:
                    service = group['Keys'][0] if len(group['Keys']) > 0 else 'Unknown'
                    region = group['Keys'][1] if len(group['Keys']) > 1 else 'Unknown'
                    usage_type = group['Keys'][2] if len(group['Keys']) > 2 else 'Unknown'
                    
                    cost_data.append({
                        'date': date,
                        'service': service,
                        'region': region,
                        'usage_type': usage_type,
                        'cost': float(group['Metrics']['BlendedCost']['Amount']),
                        'usage_quantity': float(group['Metrics']['UsageQuantity']['Amount']),
                        'currency': group['Metrics']['BlendedCost']['Unit']
                    })
            
            logger.info(f"Extracted {len(cost_data)} records from AWS")
            return cost_data
            
        except Exception as e:
            logger.error(f"Error extracting AWS cost data: {str(e)}")
            return []
    
    def extract_from_cur(self, bucket_name: str, prefix: str) -> List[Dict[str, Any]]:
        """Extrai dados do Cost and Usage Report (CUR) no S3"""
        try:
            objects = self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            cost_data = []
            
            for obj in objects.get('Contents', []):
                if obj['Key'].endswith('.csv.gz'):
                    # Baixar e processar arquivo CUR
                    response = self.s3_client.get_object(Bucket=bucket_name, Key=obj['Key'])
                    
                    # Usar pandas para ler CSV comprimido
                    df = pd.read_csv(response['Body'], compression='gzip')
                    
                    for _, row in df.iterrows():
                        cost_data.append({
                            'billing_period_start': pd.to_datetime(row.get('bill/BillingPeriodStartDate')).date(),
                            'billing_period_end': pd.to_datetime(row.get('bill/BillingPeriodEndDate')).date(),
                            'service': row.get('product/ServiceName', 'Unknown'),
                            'region': row.get('product/region', 'Unknown'),
                            'resource_id': row.get('lineItem/ResourceId', ''),
                            'usage_type': row.get('lineItem/UsageType', ''),
                            'cost': float(row.get('lineItem/BlendedCost', 0)),
                            'usage_quantity': float(row.get('lineItem/UsageAmount', 0)),
                            'currency': row.get('lineItem/CurrencyCode', 'USD'),
                            'tags': self._parse_aws_tags(row)
                        })
            
            logger.info(f"Extracted {len(cost_data)} records from AWS CUR")
            return cost_data
            
        except Exception as e:
            logger.error(f"Error extracting AWS CUR data: {str(e)}")
            return []
    
    def _parse_aws_tags(self, row) -> Dict[str, str]:
        """Processa tags do AWS CUR"""
        tags = {}
        for col in row.index:
            if col.startswith('resourceTags/user:'):
                tag_key = col.replace('resourceTags/user:', '')
                if pd.notna(row[col]):
                    tags[tag_key] = str(row[col])
        return tags
    
    def transform_to_focus(self, raw_data: List[Dict[str, Any]]) -> List[FocusCostDataCreate]:
        """Transforma dados AWS para formato FOCUS"""
        focus_data = []
        
        for record in raw_data:
            focus_record = FocusCostDataCreate(
                provider_name="AWS",
                billing_period_start=record.get('billing_period_start', record.get('date')),
                billing_period_end=record.get('billing_period_end', record.get('date')),
                service_name=record.get('service', 'Unknown'),
                region=record.get('region'),
                resource_id=record.get('resource_id'),
                effective_cost=Decimal(str(record.get('cost', 0))),
                usage_quantity=Decimal(str(record.get('usage_quantity', 0))),
                billing_currency=record.get('currency', 'USD'),
                charge_category="Usage",
                charge_frequency="Usage-Based",
                pricing_category="On-Demand",
                data_source="CUR",
                tags=record.get('tags', {})
            )
            focus_data.append(focus_record)
        
        return focus_data

class AzureConnector(CloudConnectorBase):
    """Conector para Azure Cost Management"""
    
    def __init__(self, subscription_id: str):
        super().__init__("Azure")
        self.subscription_id = subscription_id
        credential = DefaultAzureCredential()
        self.client = ConsumptionManagementClient(credential, subscription_id)
    
    def extract_cost_data(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Extrai dados de custo do Azure"""
        try:
            scope = f"/subscriptions/{self.subscription_id}"
            
            usage_details = self.client.usage_details.list(
                scope=scope,
                filter=f"properties/usageStart ge '{start_date.strftime('%Y-%m-%d')}' and properties/usageEnd le '{end_date.strftime('%Y-%m-%d')}'"
            )
            
            cost_data = []
            for usage in usage_details:
                cost_data.append({
                    'date': usage.date.date() if usage.date else None,
                    'service': usage.consumed_service or 'Unknown',
                    'resource_group': usage.resource_group or '',
                    'resource_id': usage.instance_id or '',
                    'meter_category': usage.meter_category or '',
                    'meter_subcategory': usage.meter_subcategory or '',
                    'cost': float(usage.cost or 0),
                    'usage_quantity': float(usage.quantity or 0),
                    'currency': usage.billing_currency or 'USD',
                    'tags': usage.tags or {}
                })
            
            logger.info(f"Extracted {len(cost_data)} records from Azure")
            return cost_data
            
        except Exception as e:
            logger.error(f"Error extracting Azure cost data: {str(e)}")
            return []
    
    def transform_to_focus(self, raw_data: List[Dict[str, Any]]) -> List[FocusCostDataCreate]:
        """Transforma dados Azure para formato FOCUS"""
        focus_data = []
        
        for record in raw_data:
            focus_record = FocusCostDataCreate(
                provider_name="Azure",
                billing_period_start=record.get('date'),
                billing_period_end=record.get('date'),
                service_name=record.get('service', 'Unknown'),
                service_category=record.get('meter_category'),
                resource_id=record.get('resource_id'),
                effective_cost=Decimal(str(record.get('cost', 0))),
                usage_quantity=Decimal(str(record.get('usage_quantity', 0))),
                billing_currency=record.get('currency', 'USD'),
                charge_category="Usage",
                charge_frequency="Usage-Based",
                pricing_category="On-Demand",
                data_source="Cost Management",
                tags=record.get('tags', {})
            )
            focus_data.append(focus_record)
        
        return focus_data

class GCPConnector(CloudConnectorBase):
    """Conector para Google Cloud Billing"""
    
    def __init__(self, project_id: str):
        super().__init__("GCP")
        self.project_id = project_id
        self.client = billing.CloudBillingClient()
    
    def extract_cost_data(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Extrai dados de custo do GCP via BigQuery"""
        try:
            from google.cloud import bigquery
            
            bq_client = bigquery.Client(project=self.project_id)
            
            query = f"""
            SELECT
                service.description as service_name,
                sku.description as sku_description,
                usage_start_time,
                usage_end_time,
                location.location as region,
                project.id as project_id,
                cost,
                currency,
                usage.amount as usage_quantity,
                usage.unit as usage_unit,
                labels
            FROM `{self.project_id}.cloud_billing_export.gcp_billing_export_v1_*`
            WHERE usage_start_time >= '{start_date.strftime('%Y-%m-%d')}'
            AND usage_end_time <= '{end_date.strftime('%Y-%m-%d')}'
            AND cost > 0
            """
            
            query_job = bq_client.query(query)
            results = query_job.result()
            
            cost_data = []
            for row in results:
                cost_data.append({
                    'service': row.service_name or 'Unknown',
                    'sku': row.sku_description or '',
                    'usage_start': row.usage_start_time.date() if row.usage_start_time else None,
                    'usage_end': row.usage_end_time.date() if row.usage_end_time else None,
                    'region': row.region or '',
                    'project_id': row.project_id or '',
                    'cost': float(row.cost or 0),
                    'currency': row.currency or 'USD',
                    'usage_quantity': float(row.usage_quantity or 0),
                    'usage_unit': row.usage_unit or '',
                    'labels': dict(row.labels) if row.labels else {}
                })
            
            logger.info(f"Extracted {len(cost_data)} records from GCP")
            return cost_data
            
        except Exception as e:
            logger.error(f"Error extracting GCP cost data: {str(e)}")
            return []
    
    def transform_to_focus(self, raw_data: List[Dict[str, Any]]) -> List[FocusCostDataCreate]:
        """Transforma dados GCP para formato FOCUS"""
        focus_data = []
        
        for record in raw_data:
            focus_record = FocusCostDataCreate(
                provider_name="GCP",
                billing_period_start=record.get('usage_start'),
                billing_period_end=record.get('usage_end'),
                service_name=record.get('service', 'Unknown'),
                region=record.get('region'),
                effective_cost=Decimal(str(record.get('cost', 0))),
                usage_quantity=Decimal(str(record.get('usage_quantity', 0))),
                usage_unit=record.get('usage_unit'),
                billing_currency=record.get('currency', 'USD'),
                charge_category="Usage",
                charge_frequency="Usage-Based",
                pricing_category="On-Demand",
                data_source="BigQuery Export",
                tags=record.get('labels', {})
            )
            focus_data.append(focus_record)
        
        return focus_data

class OracleCloudConnector(CloudConnectorBase):
    """Conector para Oracle Cloud Infrastructure"""
    
    def __init__(self, config_file_path: str):
        super().__init__("Oracle Cloud")
        self.config = oci.config.from_file(config_file_path)
        self.usage_client = oci.usage_api.UsageapiClient(self.config)
    
    def extract_cost_data(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Extrai dados de custo do Oracle Cloud"""
        try:
            request = oci.usage_api.models.RequestSummarizedUsagesDetails(
                tenant_id=self.config['tenancy'],
                time_usage_started=start_date,
                time_usage_ended=end_date,
                granularity='DAILY',
                group_by=['service', 'region', 'resourceId']
            )
            
            response = self.usage_client.request_summarized_usages(request)
            
            cost_data = []
            for item in response.data.items:
                cost_data.append({
                    'service': item.service or 'Unknown',
                    'region': item.region or '',
                    'resource_id': item.resource_id or '',
                    'usage_date': item.time_usage_started.date() if item.time_usage_started else None,
                    'cost': float(item.computed_amount or 0),
                    'usage_quantity': float(item.computed_quantity or 0),
                    'currency': item.currency or 'USD',
                    'tags': item.tags or {}
                })
            
            logger.info(f"Extracted {len(cost_data)} records from Oracle Cloud")
            return cost_data
            
        except Exception as e:
            logger.error(f"Error extracting Oracle Cloud cost data: {str(e)}")
            return []
    
    def transform_to_focus(self, raw_data: List[Dict[str, Any]]) -> List[FocusCostDataCreate]:
        """Transforma dados Oracle Cloud para formato FOCUS"""
        focus_data = []
        
        for record in raw_data:
            focus_record = FocusCostDataCreate(
                provider_name="Oracle Cloud",
                billing_period_start=record.get('usage_date'),
                billing_period_end=record.get('usage_date'),
                service_name=record.get('service', 'Unknown'),
                region=record.get('region'),
                resource_id=record.get('resource_id'),
                effective_cost=Decimal(str(record.get('cost', 0))),
                usage_quantity=Decimal(str(record.get('usage_quantity', 0))),
                billing_currency=record.get('currency', 'USD'),
                charge_category="Usage",
                charge_frequency="Usage-Based",
                pricing_category="On-Demand",
                data_source="Usage API",
                tags=record.get('tags', {})
            )
            focus_data.append(focus_record)
        
        return focus_data

class CloudConnectorFactory:
    """Factory para criar conectores de nuvem"""
    
    @staticmethod
    def create_connector(provider: str, **kwargs) -> CloudConnectorBase:
        """Cria o conector apropriado para o provedor"""
        if provider.lower() == "aws":
            return AWSConnector()
        elif provider.lower() == "azure":
            subscription_id = kwargs.get('subscription_id')
            if not subscription_id:
                raise ValueError("subscription_id is required for Azure connector")
            return AzureConnector(subscription_id)
        elif provider.lower() == "gcp":
            project_id = kwargs.get('project_id')
            if not project_id:
                raise ValueError("project_id is required for GCP connector")
            return GCPConnector(project_id)
        elif provider.lower() == "oracle":
            config_file = kwargs.get('config_file_path')
            if not config_file:
                raise ValueError("config_file_path is required for Oracle Cloud connector")
            return OracleCloudConnector(config_file)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

# Função utilitária para processar dados de múltiplos provedores
def extract_all_providers_data(
    start_date: datetime,
    end_date: datetime,
    providers_config: Dict[str, Dict[str, Any]]
) -> Dict[str, List[FocusCostDataCreate]]:
    """Extrai dados de todos os provedores configurados"""
    all_data = {}
    
    for provider_name, config in providers_config.items():
        try:
            connector = CloudConnectorFactory.create_connector(provider_name, **config)
            raw_data = connector.extract_cost_data(start_date, end_date)
            focus_data = connector.transform_to_focus(raw_data)
            all_data[provider_name] = focus_data
            logger.info(f"Successfully processed {len(focus_data)} records from {provider_name}")
        except Exception as e:
            logger.error(f"Failed to process {provider_name}: {str(e)}")
            all_data[provider_name] = []
    
    return all_data