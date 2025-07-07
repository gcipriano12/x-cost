"""
Analisador de distribuição de contas por provedor
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models import FocusCostData
from app.account_distribution_models import AccountDistributionItem
from datetime import date, timedelta
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class AccountDistributionAnalyzer:
    """Analisador para distribuição de contas por provedor"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_account_distribution(
        self,
        provider_name: str,
        time_filter: str = "30d",
        credential_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[AccountDistributionItem]:
        """
        Obter distribuição de contas por provedor
        
        Args:
            provider_name: Nome do provedor (ex: "Oracle Cloud", "AWS", "Azure")
            time_filter: Filtro de tempo (ex: "30d", "90d")
            credential_id: ID da credencial (opcional)
            start_date: Data inicial (opcional)
            end_date: Data final (opcional)
            
        Returns:
            Lista de AccountDistributionItem com distribuição de contas
        """
        try:
            # Calcular datas se não fornecidas
            if not start_date or not end_date:
                end_date = date.today()
                
                # Converter time_filter para dias
                if time_filter.endswith('d'):
                    days = int(time_filter[:-1])
                else:
                    days = 30  # default
                
                start_date = end_date - timedelta(days=days)
            
            logger.info(f"Analisando distribuição de contas para {provider_name} no período {start_date} a {end_date}")
            
            # Query base
            query = self.db.query(
                FocusCostData.billing_account_id,
                FocusCostData.billing_account_name,
                func.sum(FocusCostData.effective_cost).label('total_cost')
            ).filter(
                and_(
                    FocusCostData.provider_name == provider_name,
                    FocusCostData.charge_period_start >= start_date,
                    FocusCostData.charge_period_start <= end_date,
                    FocusCostData.effective_cost > 0
                )
            )
            
            # Adicionar filtro de credencial se fornecido
            if credential_id:
                # Assumindo que há um campo credential_id no modelo
                # Se não existir, esta linha pode ser removida
                if hasattr(FocusCostData, 'credential_id'):
                    query = query.filter(FocusCostData.credential_id == credential_id)
            
            # Agrupar por conta e ordenar por custo
            results = query.group_by(
                FocusCostData.billing_account_id,
                FocusCostData.billing_account_name
            ).order_by(
                func.sum(FocusCostData.effective_cost).desc()
            ).all()
            
            if not results:
                logger.warning(f"Nenhum dado encontrado para {provider_name} no período especificado")
                return []
            
            # Calcular total para porcentagens
            total_cost = sum(result.total_cost for result in results if result.total_cost)
            
            if total_cost == 0:
                logger.warning(f"Custo total zero para {provider_name}")
                return []
            
            # Criar lista de distribuição
            distribution = []
            for result in results:
                if result.total_cost and result.total_cost > 0:
                    percentage = (result.total_cost / total_cost) * 100
                    
                    # Garantir que temos um account_id válido
                    account_id = result.billing_account_id or f"account-{len(distribution)}"
                    account_name = result.billing_account_name or f"Account {account_id}"
                    
                    item = AccountDistributionItem(
                        account_id=account_id,
                        billing_account_name=account_name,
                        percentage=round(percentage, 1),
                        total_cost=round(result.total_cost, 2)
                    )
                    distribution.append(item)
            
            # Validar que soma das porcentagens é ~100%
            total_percentage = sum(item.percentage for item in distribution)
            if abs(total_percentage - 100.0) > 0.1:
                logger.warning(f"Soma das porcentagens: {total_percentage}% (esperado: 100%)")
            
            logger.info(f"Distribuição calculada: {len(distribution)} contas, total: ${total_cost:,.2f}")
            
            return distribution
            
        except Exception as e:
            logger.error(f"Erro ao calcular distribuição de contas: {e}")
            raise e
    
    def validate_provider(self, provider_name: str) -> bool:
        """Validar se o provedor existe no banco de dados"""
        try:
            count = self.db.query(func.count(FocusCostData.id)).filter(
                FocusCostData.provider_name == provider_name
            ).scalar()
            
            return count > 0
            
        except Exception as e:
            logger.error(f"Erro ao validar provedor {provider_name}: {e}")
            return False
