"""
Top Services Analytics Module

Implementa análise dos principais serviços por custo com variação temporal
"""

import logging
from datetime import date, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from decimal import Decimal

from app.models import FocusCostData, CloudProvider
from app.top_services_models import TopServiceItem, TopServicesData, TopServicesPeriod

logger = logging.getLogger(__name__)


class TopServicesAnalyzer:
    """Analisador dos principais serviços por custo"""
    
    def __init__(self, db: Session):
        self.db = db
        self.supported_providers = ["AWS", "Azure", "GCP", "Oracle Cloud"]
    
    def get_top_services(
        self,
        credential_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        provider_name: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        sort_by: str = "cost",
        sort_order: str = "desc"
    ) -> TopServicesData:
        """
        Obtém os principais serviços por custo com paginação e ordenação
        
        Args:
            credential_id: ID da credencial (para filtro futuro)
            start_date: Data início do período
            end_date: Data fim do período
            provider_name: Filtro por provider específico
            page: Número da página (inicia em 1)
            page_size: Itens por página
            sort_by: Campo para ordenação (cost, service_name, provider, change_from_previous)
            sort_order: Ordem (asc ou desc)
            
        Returns:
            TopServicesData: Dados dos principais serviços com informações de paginação
        """
        
        # Definir período padrão se não fornecido
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)  # 30 dias padrão
        
        # Validar provider
        if provider_name and provider_name not in self.supported_providers:
            raise ValueError(f"Provider '{provider_name}' não suportado. Suportados: {self.supported_providers}")
        
        # Calcular período anterior para comparação
        period_days = (end_date - start_date).days + 1
        previous_start = start_date - timedelta(days=period_days)
        previous_end = start_date - timedelta(days=1)
        
        logger.info(f"Analisando top services: {start_date} a {end_date} (vs {previous_start} a {previous_end})")
        logger.info(f"Paginação: página {page}, {page_size} itens por página")
        
        # Obter todos os custos do período atual (sem limite)
        all_current_costs = self._get_service_costs(start_date, end_date, provider_name, None)
        
        # Obter custos do período anterior
        previous_costs = self._get_service_costs(previous_start, previous_end, provider_name, None)
        
        # Calcular variações para todos os serviços
        all_services = self._calculate_variations(all_current_costs, previous_costs)
        
        # Aplicar ordenação baseada nos parâmetros
        all_services = self._apply_sorting(all_services, sort_by, sort_order)
        
        # Aplicar paginação
        total_services = len(all_services)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_services = all_services[start_idx:end_idx]
        
        # Calcular informações de paginação
        total_pages = (total_services + page_size - 1) // page_size  # Ceiling division
        has_next = page < total_pages
        has_previous = page > 1
        
        from app.top_services_models import PaginationInfo
        pagination_info = PaginationInfo(
            page=page,
            page_size=page_size,
            total_items=total_services,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous
        )
        
        return TopServicesData(
            services=paginated_services,
            total_services=total_services,
            period=TopServicesPeriod(
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat()
            ),
            pagination=pagination_info
        )
    
    def _get_service_costs(
        self,
        start_date: date,
        end_date: date,
        provider_name: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtém custos agrupados por serviço e provider para um período
        
        Returns:
            Lista de dicionários com service_name, provider, cost, region
        """
        
        # Query base
        query = self.db.query(
            FocusCostData.service_name,
            FocusCostData.provider_name,
            FocusCostData.region,
            func.sum(FocusCostData.effective_cost).label('total_cost')
        ).filter(
            and_(
                FocusCostData.charge_period_start >= start_date,
                FocusCostData.charge_period_start <= end_date,
                FocusCostData.effective_cost > 0
            )
        )
        
        # Filtrar por provider se especificado
        if provider_name:
            query = query.filter(FocusCostData.provider_name == provider_name)
        
        # Agrupar e ordenar
        query = query.group_by(
            FocusCostData.service_name,
            FocusCostData.provider_name,
            FocusCostData.region
        ).order_by(desc('total_cost'))
        
        # Não aplicar limite aqui para permitir agregação correta
        # O limite será aplicado após a agregação por serviço+provider
        
        results = query.all()
        
        # Processar resultados
        services = []
        for result in results:
            services.append({
                'service_name': result.service_name,
                'provider': result.provider_name,
                'region': result.region,
                'cost': float(result.total_cost) if result.total_cost else 0.0
            })
        
        # Agregar por serviço+provider (somar diferentes regiões)
        aggregated = self._aggregate_by_service_provider(services)
        
        # Aplicar limite final
        if limit:
            aggregated = aggregated[:limit]
        
        return aggregated
    
    def _aggregate_by_service_provider(self, services: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Agrega custos por serviço+provider, somando diferentes regiões
        """
        aggregation = {}
        
        for service in services:
            key = f"{service['service_name']}_{service['provider']}"
            
            if key not in aggregation:
                aggregation[key] = {
                    'service_name': service['service_name'],
                    'provider': service['provider'],
                    'cost': 0.0,
                    'regions': set()
                }
            
            aggregation[key]['cost'] += service['cost']
            if service['region']:
                aggregation[key]['regions'].add(service['region'])
        
        # Converter para lista e determinar região principal
        result = []
        for data in aggregation.values():
            # Região principal = primeira região (alfabética) ou None
            main_region = sorted(list(data['regions']))[0] if data['regions'] else None
            
            result.append({
                'service_name': data['service_name'],
                'provider': data['provider'],
                'cost': data['cost'],
                'region': main_region
            })
        
        # Ordenar por custo descendente
        result.sort(key=lambda x: x['cost'], reverse=True)
        
        return result
    
    def _calculate_variations(
        self,
        current_costs: List[Dict[str, Any]],
        previous_costs: List[Dict[str, Any]]
    ) -> List[TopServiceItem]:
        """
        Calcula variações percentuais entre períodos atual e anterior
        """
        
        # Criar mapa do período anterior para lookup rápido
        previous_map = {}
        for service in previous_costs:
            key = f"{service['service_name']}_{service['provider']}"
            previous_map[key] = service['cost']
        
        services = []
        for i, current in enumerate(current_costs):
            key = f"{current['service_name']}_{current['provider']}"
            previous_cost = previous_map.get(key, 0.0)
            
            # Calcular variação percentual
            if previous_cost > 0:
                change_percent = ((current['cost'] - previous_cost) / previous_cost) * 100
            else:
                # Serviço novo = 100% de aumento
                change_percent = 100.0 if current['cost'] > 0 else 0.0
            
            services.append(TopServiceItem(
                id=f"service-{i}",
                service_name=current['service_name'],
                provider=current['provider'],
                cost=current['cost'],
                change_from_previous=round(change_percent, 1),
                region=current.get('region'),
                currency="USD"
            ))
        
        return services
    
    def _count_total_services(
        self,
        start_date: date,
        end_date: date,
        provider_name: Optional[str] = None
    ) -> int:
        """
        Conta o total de serviços únicos no período
        """
        
        query = self.db.query(
            func.count(func.distinct(
                func.concat(FocusCostData.service_name, '_', FocusCostData.provider_name)
            ))
        ).filter(
            and_(
                FocusCostData.charge_period_start >= start_date,
                FocusCostData.charge_period_start <= end_date,
                FocusCostData.effective_cost > 0
            )
        )
        
        if provider_name:
            query = query.filter(FocusCostData.provider_name == provider_name)
        
        result = query.scalar()
        return result if result else 0
    
    def validate_credential(self, credential_id: str) -> bool:
        """
        Valida se a credencial existe e está ativa
        
        Placeholder para implementação futura quando integração com credenciais estiver completa
        """
        # TODO: Implementar validação real quando modelo de credenciais estiver definido
        return True
    
    def _apply_sorting(
        self, 
        services: List[TopServiceItem], 
        sort_by: str, 
        sort_order: str
    ) -> List[TopServiceItem]:
        """
        Aplica ordenação aos serviços baseada nos parâmetros
        
        Args:
            services: Lista de serviços para ordenar
            sort_by: Campo para ordenação (cost, service_name, provider, change_from_previous)
            sort_order: Ordem (asc ou desc)
            
        Returns:
            Lista ordenada de serviços
        """
        logger.info(f"Applying sorting: {sort_by} {sort_order}")
        
        # Definir função de ordenação baseada no campo
        if sort_by == "cost":
            key_func = lambda x: x.cost
        elif sort_by == "service_name":
            key_func = lambda x: x.service_name.lower()  # Case insensitive
        elif sort_by == "provider":
            key_func = lambda x: x.provider.lower()  # Case insensitive
        elif sort_by == "change_from_previous":
            key_func = lambda x: x.change_from_previous
        else:
            # Fallback para cost se campo inválido
            logger.warning(f"Invalid sort field '{sort_by}', falling back to 'cost'")
            key_func = lambda x: x.cost
        
        # Determinar ordem (desc = reverse=True, asc = reverse=False)
        reverse = sort_order.lower() == "desc"
        
        # Aplicar ordenação
        sorted_services = sorted(services, key=key_func, reverse=reverse)
        
        logger.info(f"Sorted {len(sorted_services)} services by {sort_by} {sort_order}")
        
        return sorted_services
