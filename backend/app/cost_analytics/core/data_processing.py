"""
Data Processing Module

Módulo para processamento e categorização de dados de custo
"""

from typing import Dict, List, Optional


class ServiceCategoryMapper:
    """
    Mapeador de serviços cloud para categorias funcionais
    """
    
    # Mapeamento expandido de serviços para categorias
    SERVICE_CATEGORY_MAPPING = {
        # Computation
        "EC2": "Computation",
        "Virtual Machines": "Computation", 
        "Compute Engine": "Computation",
        "Lambda": "Computation",
        "Functions": "Computation",
        "Cloud Functions": "Computation",
        "App Service": "Computation",
        "Cloud Run": "Computation",
        "Container Instances": "Computation",
        "ECS": "Computation",
        "EKS": "Computation",
        "AKS": "Computation",
        "GKE": "Computation",
        "Fargate": "Computation",
        "Batch": "Computation",
        
        # Storage
        "S3": "Storage",
        "Storage Account": "Storage",
        "Cloud Storage": "Storage", 
        "EBS": "Storage",
        "Storage": "Storage",
        "Blob Storage": "Storage",
        "File Storage": "Storage",
        "EFS": "Storage",
        "FSx": "Storage",
        "Persistent Disk": "Storage",
        "Glacier": "Storage",
        "Archive Storage": "Storage",
        
        # Database
        "RDS": "Database",
        "SQL Database": "Database",
        "Cloud SQL": "Database",
        "DynamoDB": "Database",
        "CosmosDB": "Database", 
        "BigQuery": "Database",
        "Firestore": "Database",
        "DocumentDB": "Database",
        "Aurora": "Database",
        "ElastiCache": "Database",
        "Redis": "Database",
        "Memorystore": "Database",
        "Table Storage": "Database",
        
        # Network
        "CloudFront": "Network",
        "CDN": "Network", 
        "Cloud CDN": "Network",
        "VPC": "Network",
        "Load Balancer": "Network",
        "ELB": "Network",
        "ALB": "Network",
        "NLB": "Network",
        "Application Gateway": "Network",
        "ExpressRoute": "Network",
        "Direct Connect": "Network",
        "Cloud NAT": "Network",
        "NAT Gateway": "Network",
        "API Gateway": "Network",
        "Transit Gateway": "Network",
        
        # Monitoring & Management
        "CloudWatch": "Monitoring",
        "Monitor": "Monitoring", 
        "Monitoring": "Monitoring",
        "Log Analytics": "Monitoring",
        "Application Insights": "Monitoring",
        "Cloud Logging": "Monitoring",
        "Cloud Monitoring": "Monitoring",
        "CloudTrail": "Monitoring",
        "Config": "Monitoring",
        "Systems Manager": "Monitoring",
        
        # Security
        "IAM": "Security",
        "Key Vault": "Security",
        "Security Center": "Security", 
        "WAF": "Security",
        "GuardDuty": "Security",
        "Security Command Center": "Security",
        "KMS": "Security",
        "Certificate Manager": "Security",
        "Secrets Manager": "Security",
        "Shield": "Security",
        
        # AI/ML
        "SageMaker": "AI/ML",
        "Machine Learning": "AI/ML",
        "Cognitive Services": "AI/ML",
        "AI Platform": "AI/ML",
        "AutoML": "AI/ML",
        "Comprehend": "AI/ML",
        "Textract": "AI/ML",
        "Rekognition": "AI/ML",
        "Translate": "AI/ML",
        "Polly": "AI/ML",
        
        # Analytics
        "Redshift": "Analytics",
        "BigQuery": "Analytics", 
        "Synapse Analytics": "Analytics",
        "Data Factory": "Analytics",
        "Dataflow": "Analytics",
        "Kinesis": "Analytics",
        "EMR": "Analytics",
        "Glue": "Analytics",
        "QuickSight": "Analytics",
        "Athena": "Analytics",
        "Data Lake": "Analytics",
        
        # Integration
        "SQS": "Integration",
        "SNS": "Integration",
        "Service Bus": "Integration",
        "Event Hubs": "Integration",
        "Pub/Sub": "Integration",
        "Step Functions": "Integration",
        "Logic Apps": "Integration",
        
        # Developer Tools
        "CodeBuild": "Developer Tools",
        "CodePipeline": "Developer Tools",
        "CodeCommit": "Developer Tools",
        "DevOps": "Developer Tools",
        "Cloud Build": "Developer Tools",
        "Source Repositories": "Developer Tools",
        
        # Default fallback
        "_default": "Others"
    }
    
    def __init__(self, custom_mapping: Optional[Dict[str, str]] = None):
        """
        Inicializa o mapeador de categorias
        
        Args:
            custom_mapping: Mapeamento personalizado adicional
        """
        self.mapping = self.SERVICE_CATEGORY_MAPPING.copy()
        if custom_mapping:
            self.mapping.update(custom_mapping)
    
    def get_category(self, service_name: str) -> str:
        """
        Mapeia nome do serviço para categoria
        
        Args:
            service_name: Nome do serviço cloud
            
        Returns:
            Categoria do serviço
        """
        if not service_name:
            return "Others"
        
        # Busca exata primeiro
        if service_name in self.mapping:
            return self.mapping[service_name]
        
        # Busca por substring (case insensitive)
        service_lower = service_name.lower()
        for service_key, category in self.mapping.items():
            if service_key != "_default" and service_key.lower() in service_lower:
                return category
        
        # Fallback para "Others"
        return self.mapping["_default"]
    
    def get_categories(self) -> List[str]:
        """Retorna lista de todas as categorias disponíveis"""
        categories = set(self.mapping.values())
        categories.discard("Others")  # Remove Others para listá-lo por último
        return sorted(list(categories)) + ["Others"]
    
    def get_services_by_category(self, category: str) -> List[str]:
        """Retorna lista de serviços de uma categoria específica"""
        return [
            service for service, cat in self.mapping.items() 
            if cat == category and service != "_default"
        ]
    
    def add_custom_mapping(self, service: str, category: str) -> None:
        """Adiciona mapeamento personalizado"""
        self.mapping[service] = category
    
    def get_category_distribution(self, services: List[str]) -> Dict[str, int]:
        """
        Calcula distribuição de categorias para uma lista de serviços
        
        Args:
            services: Lista de nomes de serviços
            
        Returns:
            Dicionário com contagem por categoria
        """
        distribution = {}
        for service in services:
            category = self.get_category(service)
            distribution[category] = distribution.get(category, 0) + 1
        
        return distribution


# Instância global do mapeador
_default_mapper = ServiceCategoryMapper()


def get_service_category(service_name: str) -> str:
    """
    Função de conveniência para mapeamento de categoria
    
    Args:
        service_name: Nome do serviço
        
    Returns:
        Categoria do serviço
    """
    return _default_mapper.get_category(service_name)


def get_all_categories() -> List[str]:
    """Retorna todas as categorias disponíveis"""
    return _default_mapper.get_categories()


def get_services_by_category(category: str) -> List[str]:
    """Retorna serviços de uma categoria específica"""
    return _default_mapper.get_services_by_category(category)


class DataNormalizer:
    """
    Classe para normalização e limpeza de dados de custo
    """
    
    @staticmethod
    def normalize_provider_name(provider: str) -> str:
        """Normaliza nomes de provedores"""
        if not provider:
            return "Unknown"
        
        provider_mapping = {
            "amazon web services": "AWS",
            "aws": "AWS", 
            "microsoft azure": "Azure",
            "azure": "Azure",
            "google cloud platform": "GCP",
            "google cloud": "GCP",
            "gcp": "GCP",
            "oracle cloud": "Oracle",
            "oracle": "Oracle",
            "oci": "Oracle"
        }
        
        provider_lower = provider.lower().strip()
        return provider_mapping.get(provider_lower, provider.title())
    
    @staticmethod
    def normalize_currency_code(currency: str) -> str:
        """Normaliza códigos de moeda"""
        if not currency:
            return "USD"
        
        currency = currency.upper().strip()
        valid_currencies = {"USD", "EUR", "GBP", "BRL", "JPY", "CAD", "AUD"}
        
        return currency if currency in valid_currencies else "USD"
    
    @staticmethod
    def clean_service_name(service_name: str) -> str:
        """Limpa e normaliza nomes de serviços"""
        if not service_name:
            return "Unknown"
        
        # Remove prefixos/sufixos comuns
        service = service_name.strip()
        prefixes_to_remove = ["Amazon ", "Microsoft ", "Google ", "Oracle "]
        
        for prefix in prefixes_to_remove:
            if service.startswith(prefix):
                service = service[len(prefix):]
        
        return service.strip()
    
    @staticmethod
    def normalize_region_name(region: str, provider: str = None) -> str:
        """Normaliza nomes de regiões"""
        if not region:
            return "Unknown"
        
        region = region.strip()
        
        # Mapeamentos específicos por provedor
        if provider and provider.upper() == "AWS":
            aws_mapping = {
                "us-east-1": "US East (N. Virginia)",
                "us-west-2": "US West (Oregon)",
                "eu-west-1": "Europe (Ireland)",
                "ap-southeast-1": "Asia Pacific (Singapore)"
            }
            return aws_mapping.get(region, region)
        
        return region