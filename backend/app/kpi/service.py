"""
KPI Service - X Cost
Serviço principal para gerenciamento de KPIs
"""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.kpi.models import (
    KPIDefinition, KPIResult, KPICompanyConfig,
    KPICategory, KPIValueResponse, KPICategoryResponse,
    KPIHistoryResponse, KPICompanyConfigResponse
)
from app.kpi.calculator import KPICalculator

logger = logging.getLogger(__name__)

class KPIService:
    """Serviço principal de KPIs"""
    
    def __init__(self, db: Session):
        self.db = db
        self.calculator = KPICalculator(db)
        
    def get_current_kpis(self, category: Optional[KPICategory] = None) -> List[KPIValueResponse]:
        """Obtém valores atuais de todos os KPIs"""
        try:
            # Buscar KPIs ativos
            query = self.db.query(KPIDefinition).filter(
                KPIDefinition.is_active == True
            )
            
            if category:
                query = query.filter(KPIDefinition.category == category)
                
            kpis = query.all()
            
            # Buscar últimos resultados
            results = []
            for kpi in kpis:
                # Buscar último resultado
                last_result = self.db.query(KPIResult).filter(
                    KPIResult.kpi_definition_id == kpi.id
                ).order_by(KPIResult.calculation_date.desc()).first()
                
                # Buscar configuração da empresa para o target
                config = self.db.query(KPICompanyConfig).filter(
                    KPICompanyConfig.kpi_definition_id == kpi.id,
                    KPICompanyConfig.company_id == 'default'
                ).first()
                
                target_value = config.target_value if config else None
                
                if last_result:
                    status = self._determine_status(kpi, last_result.value, config)
                    
                    results.append(KPIValueResponse(
                        kpi_id=kpi.id,
                        code=kpi.code,
                        name=kpi.name,
                        category=kpi.category,
                        value=last_result.value,
                        unit=kpi.unit,
                        target=target_value,
                        trend=last_result.trend,
                        is_good_when_higher=kpi.is_good_when_higher,
                        status=status,
                        last_updated=last_result.created_at,
                        metadata=last_result.meta_data
                    ))
                else:
                    # Se não há resultado, calcular agora
                    try:
                        value = self.calculator._calculate_kpi(kpi, date.today())
                        if value is not None:
                            status = self._determine_status(kpi, value, config)
                            
                            results.append(KPIValueResponse(
                                kpi_id=kpi.id,
                                code=kpi.code,
                                name=kpi.name,
                                category=kpi.category,
                                value=value,
                                unit=kpi.unit,
                                target=target_value,
                                trend=None,
                                is_good_when_higher=kpi.is_good_when_higher,
                                status=status,
                                last_updated=datetime.utcnow(),
                                metadata={'calculated_on_demand': True}
                            ))
                    except Exception as e:
                        logger.error(f"Error calculating KPI {kpi.code} on demand: {str(e)}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting current KPIs: {str(e)}")
            return []
    
    def get_kpis_by_category(self) -> List[KPICategoryResponse]:
        """Obtém KPIs agrupados por categoria"""
        try:
            categories = []
            
            for category in KPICategory:
                kpis = self.get_current_kpis(category=category)
                
                if kpis:
                    # Calcular resumo da categoria
                    summary = self._calculate_category_summary(kpis)
                    
                    categories.append(KPICategoryResponse(
                        category=category,
                        kpis=kpis,
                        summary=summary
                    ))
                    
            return categories
            
        except Exception as e:
            logger.error(f"Error getting KPIs by category: {str(e)}")
            return []
    
    def calculate_kpis(self, calculation_date: Optional[date] = None) -> Dict[str, Any]:
        """Executa cálculo de todos os KPIs"""
        try:
            if not calculation_date:
                calculation_date = date.today()
                
            logger.info(f"Starting KPI calculation for {calculation_date}")
            
            results = self.calculator.calculate_all_kpis(calculation_date)
            
            # Contar sucessos e erros
            success_count = len([r for r in results.values() if 'error' not in r])
            error_count = len(results) - success_count
            
            logger.info(f"KPI calculation completed: {success_count} success, {error_count} errors")
            
            return {
                'calculation_date': calculation_date,
                'results': results,
                'success_count': success_count,
                'error_count': error_count,
                'total_kpis': len(results)
            }
            
        except Exception as e:
            logger.error(f"Error calculating KPIs: {str(e)}")
            return {
                'calculation_date': calculation_date or date.today(),
                'results': {},
                'success_count': 0,
                'error_count': 0,
                'error': str(e)
            }
    
    def get_kpi_history(
        self, 
        kpi_code: str, 
        start_date: date, 
        end_date: date
    ) -> List[KPIHistoryResponse]:
        """Obtém histórico de um KPI"""
        try:
            # Buscar definição
            kpi = self.db.query(KPIDefinition).filter(
                KPIDefinition.code == kpi_code
            ).first()
            
            if not kpi:
                logger.warning(f"KPI not found: {kpi_code}")
                return []
                
            # Buscar resultados
            results = self.db.query(KPIResult).filter(
                and_(
                    KPIResult.kpi_id == kpi.id,
                    KPIResult.calculation_date >= start_date,
                    KPIResult.calculation_date <= end_date
                )
            ).order_by(KPIResult.calculation_date).all()
            
            history = []
            for r in results:
                history.append(KPIHistoryResponse(
                    date=r.calculation_date,
                    value=float(r.value),
                    trend=float(r.trend) if r.trend else 0,
                    metadata=r.metadata
                ))
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting KPI history for {kpi_code}: {str(e)}")
            return []
    
    def get_kpi_by_code(self, kpi_code: str) -> Optional[KPIValueResponse]:
        """Obtém um KPI específico pelo código"""
        try:
            kpis = self.get_current_kpis()
            for kpi in kpis:
                if kpi.code == kpi_code:
                    return kpi
            return None
            
        except Exception as e:
            logger.error(f"Error getting KPI by code {kpi_code}: {str(e)}")
            return None
    
    def update_kpi_config(
        self,
        kpi_code: str,
        company_id: str,
        target_value: Optional[float] = None,
        warning_threshold: Optional[float] = None,
        critical_threshold: Optional[float] = None,
        is_enabled: Optional[bool] = None
    ) -> Optional[KPICompanyConfigResponse]:
        """Atualiza configuração de KPI para empresa"""
        try:
            # Buscar KPI
            kpi = self.db.query(KPIDefinition).filter(
                KPIDefinition.code == kpi_code
            ).first()
            
            if not kpi:
                raise ValueError(f"KPI {kpi_code} not found")
                
            # Buscar ou criar config
            config = self.db.query(KPICompanyConfig).filter(
                and_(
                    KPICompanyConfig.kpi_id == kpi.id,
                    KPICompanyConfig.company_id == company_id
                )
            ).first()
            
            if not config:
                config = KPICompanyConfig(
                    kpi_id=kpi.id,
                    company_id=company_id
                )
                self.db.add(config)
                
            # Atualizar valores
            if target_value is not None:
                config.target_value = target_value
            if warning_threshold is not None:
                config.warning_threshold = warning_threshold
            if critical_threshold is not None:
                config.critical_threshold = critical_threshold
            if is_enabled is not None:
                config.is_enabled = is_enabled
                
            config.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            return KPICompanyConfigResponse(
                id=config.id,
                kpi_id=config.kpi_id,
                company_id=config.company_id,
                target_value=config.target_value,
                warning_threshold=config.warning_threshold,
                critical_threshold=config.critical_threshold,
                is_enabled=config.is_enabled,
                notification_settings=config.notification_settings,
                created_at=config.created_at,
                updated_at=config.updated_at
            )
            
        except Exception as e:
            logger.error(f"Error updating KPI config: {str(e)}")
            self.db.rollback()
            return None
    
    def get_kpi_definitions(self, category: Optional[KPICategory] = None) -> List[KPIDefinition]:
        """Lista todas as definições de KPIs disponíveis"""
        try:
            query = self.db.query(KPIDefinition).filter(
                KPIDefinition.is_active == True
            )
            
            if category:
                query = query.filter(KPIDefinition.category == category)
                
            return query.all()
            
        except Exception as e:
            logger.error(f"Error getting KPI definitions: {str(e)}")
            return []
    
    def get_kpi_dashboard_summary(self) -> Dict[str, Any]:
        """Obtém resumo geral dos KPIs para dashboard"""
        try:
            categories = self.get_kpis_by_category()
            
            total_kpis = sum(len(cat.kpis) for cat in categories)
            
            # Contar status geral
            all_kpis = []
            for cat in categories:
                all_kpis.extend(cat.kpis)
            
            status_counts = {
                'good': len([k for k in all_kpis if k.status == 'good']),
                'warning': len([k for k in all_kpis if k.status == 'warning']),
                'critical': len([k for k in all_kpis if k.status == 'critical']),
                'neutral': len([k for k in all_kpis if k.status == 'neutral'])
            }
            
            # Calcular health score geral
            if total_kpis > 0:
                health_score = (status_counts['good'] / total_kpis) * 100
            else:
                health_score = 0
            
            # Top KPIs com problemas
            problem_kpis = [k for k in all_kpis if k.status in ['warning', 'critical']]
            problem_kpis.sort(key=lambda x: (x.status == 'critical', abs(float(x.trend or 0))), reverse=True)
            
            return {
                'total_kpis': total_kpis,
                'health_score': round(health_score, 1),
                'status_distribution': status_counts,
                'categories': categories,
                'top_problem_kpis': problem_kpis[:5],
                'last_calculation': max([k.last_updated for k in all_kpis]) if all_kpis else None
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard summary: {str(e)}")
            return {
                'total_kpis': 0,
                'health_score': 0,
                'status_distribution': {'good': 0, 'warning': 0, 'critical': 0, 'neutral': 0},
                'categories': [],
                'top_problem_kpis': [],
                'error': str(e)
            }
    
    def _calculate_category_summary(self, kpis: List[KPIValueResponse]) -> Dict[str, Any]:
        """Calcula resumo de uma categoria de KPIs"""
        try:
            total = len(kpis)
            if total == 0:
                return {
                    'total_kpis': 0,
                    'status_distribution': {'good': 0, 'warning': 0, 'critical': 0, 'neutral': 0},
                    'health_score': 0,
                    'average_trend': 0
                }
            
            good = len([k for k in kpis if k.status == 'good'])
            warning = len([k for k in kpis if k.status == 'warning'])
            critical = len([k for k in kpis if k.status == 'critical'])
            neutral = len([k for k in kpis if k.status == 'neutral'])
            
            # Calcular score geral (0-100)
            score = (good / total * 100) if total > 0 else 0
            
            # Trend médio
            trends = [float(k.trend or 0) for k in kpis]
            avg_trend = sum(trends) / len(trends) if trends else 0
            
            return {
                'total_kpis': total,
                'status_distribution': {
                    'good': good,
                    'warning': warning,
                    'critical': critical,
                    'neutral': neutral
                },
                'health_score': round(score, 1),
                'average_trend': round(avg_trend, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating category summary: {str(e)}")
            return {
                'total_kpis': 0,
                'status_distribution': {'good': 0, 'warning': 0, 'critical': 0, 'neutral': 0},
                'health_score': 0,
                'average_trend': 0
            }
    
    def _determine_status(self, kpi: KPIDefinition, value, config: Optional[KPICompanyConfig] = None) -> str:
        """Determina status do KPI baseado no valor e configuração"""
        try:
            if not config or not config.target_value:
                return 'neutral'
                
            target = float(config.target_value)
            current = float(value)
            
            # Usar thresholds customizados se disponíveis
            warning_threshold = float(config.warning_threshold) if config.warning_threshold else target * 0.8
            critical_threshold = float(config.critical_threshold) if config.critical_threshold else target * 0.6
            
            if kpi.is_good_when_higher:
                if current >= target:
                    return 'good'
                elif current >= warning_threshold:
                    return 'warning'
                else:
                    return 'critical'
            else:
                # Para KPIs onde menor é melhor (ex: waste percentage)
                if current <= target:
                    return 'good'
                elif current <= warning_threshold:
                    return 'warning'
                else:
                    return 'critical'
                    
        except Exception as e:
            logger.error(f"Error determining status for KPI {kpi.code}: {str(e)}")
            return 'neutral'
