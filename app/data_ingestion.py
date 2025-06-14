from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import logging
import pandas as pd
from decimal import Decimal

from app.models import FocusCostData, FocusCostDataCreate, CostAnalysis, AnalysisType
from app.database import cache_manager

logger = logging.getLogger(__name__)

class DataIngestionService:
    """Serviço para ingestão e processamento de dados de custo"""
    
    def __init__(self, db: Session):
        self.db = db
        self.batch_size = 1000  # Tamanho do lote para inserções em massa
    
    def bulk_insert_focus_data(self, focus_data_list: List[FocusCostDataCreate]) -> int:
        """Inserção em massa de dados FOCUS"""
        try:
            if not focus_data_list:
                return 0
            
            # Converter para modelos SQLAlchemy
            db_objects = []
            for focus_data in focus_data_list:
                # Verificar se o registro já existe (evitar duplicatas)
                existing = self.db.query(FocusCostData).filter(
                    and_(
                        FocusCostData.provider_name == focus_data.provider_name,
                        FocusCostData.service_name == focus_data.service_name,
                        FocusCostData.billing_period_start == focus_data.billing_period_start,
                        FocusCostData.resource_id == focus_data.resource_id,
                        FocusCostData.effective_cost == focus_data.effective_cost
                    )
                ).first()
                
                if not existing:
                    db_obj = FocusCostData(**focus_data.dict())
                    db_objects.append(db_obj)
            
            if not db_objects:
                logger.info("No new records to insert (all duplicates)")
                return 0
            
            # Inserção em lotes
            inserted_count = 0
            for i in range(0, len(db_objects), self.batch_size):
                batch = db_objects[i:i + self.batch_size]
                self.db.add_all(batch)
                
                try:
                    self.db.commit()
                    inserted_count += len(batch)
                    logger.info(f"Inserted batch {i//self.batch_size + 1}: {len(batch)} records")
                except Exception as e:
                    logger.error(f"Error inserting batch {i//self.batch_size + 1}: {str(e)}")
                    self.db.rollback()
                    
                    # Tentar inserir registros individualmente para identificar problemas
                    for obj in batch:
                        try:
                            self.db.add(obj)
                            self.db.commit()
                            inserted_count += 1
                        except Exception as individual_error:
                            logger.error(f"Error inserting individual record: {str(individual_error)}")
                            self.db.rollback()
            
            # Limpar cache relacionado
            cache_manager.clear_pattern("costs:*")
            cache_manager.clear_pattern("summary:*")
            cache_manager.clear_pattern("system_metrics")
            
            logger.info(f"Successfully inserted {inserted_count} records out of {len(focus_data_list)} provided")
            return inserted_count
            
        except Exception as e:
            logger.error(f"Error in bulk insert: {str(e)}")
            self.db.rollback()
            return 0
    
    def update_cost_analyses(self, provider_name: Optional[str] = None) -> bool:
        """Atualiza análises de custo pré-calculadas"""
        try:
            from cost_analytics import CostAnalyzer
            
            analyzer = CostAnalyzer(self.db)
            
            # Calcular análises para o último mês
            end_date = date.today()
            start_date = date(end_date.year, end_date.month, 1)  # Primeiro dia do mês
            
            # Análise de tendência mensal
            trend_data = analyzer.calculate_cost_trend(
                provider_name=provider_name,
                start_date=start_date,
                end_date=end_date,
                period="daily"
            )
            
            # Salvar análises de tendência
            for trend in trend_data[-30:]:  # Últimos 30 dias
                if trend.get('period') and trend.get('total_cost'):
                    analysis = CostAnalysis(
                        analysis_type=AnalysisType.TREND,
                        provider_name=provider_name,
                        period_start=trend['period'],
                        period_end=trend['period'],
                        total_cost=Decimal(str(trend['total_cost'])),
                        cost_trend=Decimal(str(trend.get('trend_percentage', 0)))
                    )
                    
                    # Verificar se já existe
                    existing = self.db.query(CostAnalysis).filter(
                        and_(
                            CostAnalysis.analysis_type == AnalysisType.TREND,
                            CostAnalysis.provider_name == provider_name,
                            CostAnalysis.period_start == trend['period']
                        )
                    ).first()
                    
                    if existing:
                        existing.total_cost = analysis.total_cost
                        existing.cost_trend = analysis.cost_trend
                        existing.calculation_date = datetime.utcnow()
                    else:
                        self.db.add(analysis)
            
            # Análise de previsão
            forecast_data = analyzer.forecast_costs(
                provider_name=provider_name,
                forecast_days=30,
                historical_days=60
            )
            
            if 'daily_forecasts' in forecast_data:
                for forecast in forecast_data['daily_forecasts']:
                    analysis = CostAnalysis(
                        analysis_type=AnalysisType.FORECAST,
                        provider_name=provider_name,
                        period_start=forecast['date'],
                        period_end=forecast['date'],
                        forecasted_cost=Decimal(str(forecast['forecasted_cost']))
                    )
                    
                    existing = self.db.query(CostAnalysis).filter(
                        and_(
                            CostAnalysis.analysis_type == AnalysisType.FORECAST,
                            CostAnalysis.provider_name == provider_name,
                            CostAnalysis.period_start == forecast['date']
                        )
                    ).first()
                    
                    if existing:
                        existing.forecasted_cost = analysis.forecasted_cost
                        existing.calculation_date = datetime.utcnow()
                    else:
                        self.db.add(analysis)
            
            self.db.commit()
            
            # Limpar cache de análises
            cache_manager.clear_pattern("cost_trend:*")
            cache_manager.clear_pattern("cost_forecast:*")
            
            logger.info(f"Updated cost analyses for provider: {provider_name or 'All'}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating cost analyses: {str(e)}")
            self.db.rollback()
            return False
    
    def validate_focus_data(self, focus_data: FocusCostDataCreate) -> Dict[str, Any]:
        """Valida dados FOCUS antes da inserção"""
        errors = []
        warnings = []
        
        # Validações obrigatórias
        if not focus_data.provider_name:
            errors.append("provider_name is required")
        
        if not focus_data.service_name:
            errors.append("service_name is required")
        
        if not focus_data.billing_period_start:
            errors.append("billing_period_start is required")
        
        if not focus_data.billing_period_end:
            errors.append("billing_period_end is required")
        
        # Validações de negócio
        if focus_data.billing_period_start and focus_data.billing_period_end:
            if focus_data.billing_period_start > focus_data.billing_period_end:
                errors.append("billing_period_start cannot be after billing_period_end")
        
        if focus_data.effective_cost and focus_data.effective_cost < 0:
            warnings.append("negative effective_cost detected")
        
        if focus_data.usage_quantity and focus_data.usage_quantity < 0:
            warnings.append("negative usage_quantity detected")
        
        # Validações de formato
        if focus_data.billing_currency and len(focus_data.billing_currency) != 3:
            warnings.append("billing_currency should be 3-letter ISO code")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def process_and_validate_batch(self, focus_data_list: List[FocusCostDataCreate]) -> Dict[str, Any]:
        """Processa e valida um lote de dados FOCUS"""
        valid_records = []
        invalid_records = []
        total_warnings = 0
        
        for i, focus_data in enumerate(focus_data_list):
            validation_result = self.validate_focus_data(focus_data)
            
            if validation_result["is_valid"]:
                valid_records.append(focus_data)
                total_warnings += len(validation_result["warnings"])
            else:
                invalid_records.append({
                    "index": i,
                    "data": focus_data.dict(),
                    "errors": validation_result["errors"],
                    "warnings": validation_result["warnings"]
                })
        
        return {
            "total_records": len(focus_data_list),
            "valid_records": len(valid_records),
            "invalid_records": len(invalid_records),
            "total_warnings": total_warnings,
            "valid_data": valid_records,
            "invalid_data": invalid_records
        }
    
    def cleanup_old_data(self, retention_days: int = 730) -> int:
        """Remove dados antigos (padrão: 2 anos)"""
        try:
            cutoff_date = date.today() - pd.Timedelta(days=retention_days)
            
            deleted = self.db.query(FocusCostData).filter(
                FocusCostData.billing_period_start < cutoff_date
            ).delete()
            
            self.db.commit()
            
            # Limpar cache
            cache_manager.clear_pattern("*")
            
            logger.info(f"Cleaned up {deleted} records older than {retention_days} days")
            return deleted
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {str(e)}")
            self.db.rollback()
            return 0
    
    def get_ingestion_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas de ingestão"""
        try:
            from sqlalchemy import func
            
            # Estatísticas gerais
            total_records = self.db.query(func.count(FocusCostData.id)).scalar()
            
            # Por provedor
            provider_stats = self.db.query(
                FocusCostData.provider_name,
                func.count(FocusCostData.id).label('count'),
                func.min(FocusCostData.billing_period_start).label('oldest_date'),
                func.max(FocusCostData.billing_period_end).label('newest_date'),
                func.sum(FocusCostData.effective_cost).label('total_cost')
            ).group_by(FocusCostData.provider_name).all()
            
            # Registros por dia (últimos 30 dias)
            thirty_days_ago = date.today() - pd.Timedelta(days=30)
            daily_stats = self.db.query(
                func.date(FocusCostData.created_at).label('date'),
                func.count(FocusCostData.id).label('records_added')
            ).filter(
                FocusCostData.created_at >= thirty_days_ago
            ).group_by(
                func.date(FocusCostData.created_at)
            ).order_by(
                func.date(FocusCostData.created_at).desc()
            ).all()
            
            return {
                "total_records": total_records,
                "providers": [
                    {
                        "provider_name": stat.provider_name,
                        "record_count": stat.count,
                        "oldest_date": stat.oldest_date,
                        "newest_date": stat.newest_date,
                        "total_cost": float(stat.total_cost or 0)
                    }
                    for stat in provider_stats
                ],
                "daily_ingestion": [
                    {
                        "date": stat.date,
                        "records_added": stat.records_added
                    }
                    for stat in daily_stats
                ],
                "generated_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error getting ingestion stats: {str(e)}")
            return {"error": str(e)}
    
    def reconcile_data(self, provider_name: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """Reconcilia dados de um provedor para um período específico"""
        try:
            # Obter dados do banco
            db_data = self.db.query(FocusCostData).filter(
                and_(
                    FocusCostData.provider_name == provider_name,
                    FocusCostData.billing_period_start >= start_date,
                    FocusCostData.billing_period_end <= end_date
                )
            ).all()
            
            # Agrupar por dia
            daily_costs = {}
            for record in db_data:
                day = record.billing_period_start
                if day not in daily_costs:
                    daily_costs[day] = 0
                daily_costs[day] += float(record.effective_cost or 0)
            
            # Identificar dias com dados faltantes
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')
            missing_dates = []
            
            for single_date in date_range:
                if single_date.date() not in daily_costs:
                    missing_dates.append(single_date.date())
            
            return {
                "provider_name": provider_name,
                "period": {"start": start_date, "end": end_date},
                "total_records": len(db_data),
                "total_cost": sum(daily_costs.values()),
                "days_with_data": len(daily_costs),
                "missing_dates": missing_dates,
                "daily_costs": {str(k): v for k, v in daily_costs.items()},
                "reconciliation_date": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error reconciling data: {str(e)}")
            return {"error": str(e)}

class DataQualityChecker:
    """Verificador de qualidade dos dados"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def run_quality_checks(self) -> Dict[str, Any]:
        """Executa verificações de qualidade dos dados"""
        try:
            checks = {}
            
            # Check 1: Registros com custo negativo
            negative_cost_count = self.db.query(FocusCostData).filter(
                FocusCostData.effective_cost < 0
            ).count()
            checks["negative_costs"] = {
                "count": negative_cost_count,
                "status": "pass" if negative_cost_count == 0 else "warning"
            }
            
            # Check 2: Registros sem provider_name
            missing_provider_count = self.db.query(FocusCostData).filter(
                or_(FocusCostData.provider_name.is_(None), FocusCostData.provider_name == "")
            ).count()
            checks["missing_provider"] = {
                "count": missing_provider_count,
                "status": "pass" if missing_provider_count == 0 else "fail"
            }
            
            # Check 3: Registros sem service_name
            missing_service_count = self.db.query(FocusCostData).filter(
                or_(FocusCostData.service_name.is_(None), FocusCostData.service_name == "")
            ).count()
            checks["missing_service"] = {
                "count": missing_service_count,
                "status": "pass" if missing_service_count == 0 else "fail"
            }
            
            # Check 4: Períodos de billing inválidos
            invalid_period_count = self.db.query(FocusCostData).filter(
                FocusCostData.billing_period_start > FocusCostData.billing_period_end
            ).count()
            checks["invalid_periods"] = {
                "count": invalid_period_count,
                "status": "pass" if invalid_period_count == 0 else "fail"
            }
            
            # Check 5: Registros duplicados
            from sqlalchemy import func
            duplicate_check = self.db.query(
                FocusCostData.provider_name,
                FocusCostData.service_name,
                FocusCostData.resource_id,
                FocusCostData.billing_period_start,
                func.count(FocusCostData.id).label('count')
            ).group_by(
                FocusCostData.provider_name,
                FocusCostData.service_name,
                FocusCostData.resource_id,
                FocusCostData.billing_period_start
            ).having(func.count(FocusCostData.id) > 1).count()
            
            checks["duplicates"] = {
                "count": duplicate_check,
                "status": "pass" if duplicate_check == 0 else "warning"
            }
            
            # Check 6: Completude de dados por provedor (últimos 7 dias)
            seven_days_ago = date.today() - pd.Timedelta(days=7)
            completeness_check = {}
            
            providers = self.db.query(FocusCostData.provider_name).distinct().all()
            for provider in providers:
                provider_name = provider.provider_name
                days_with_data = self.db.query(
                    func.date(FocusCostData.billing_period_start)
                ).filter(
                    and_(
                        FocusCostData.provider_name == provider_name,
                        FocusCostData.billing_period_start >= seven_days_ago
                    )
                ).distinct().count()
                
                completeness_check[provider_name] = {
                    "days_with_data": days_with_data,
                    "expected_days": 7,
                    "completeness_percentage": (days_with_data / 7) * 100
                }
            
            checks["data_completeness"] = completeness_check
            
            # Calcular score geral de qualidade
            total_checks = len([c for c in checks.values() if isinstance(c, dict) and 'status' in c])
            passed_checks = len([c for c in checks.values() if isinstance(c, dict) and c.get('status') == 'pass'])
            quality_score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
            
            return {
                "checks": checks,
                "quality_score": quality_score,
                "total_checks": total_checks,
                "passed_checks": passed_checks,
                "checked_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error running quality checks: {str(e)}")
            return {"error": str(e)}
    
    def get_data_freshness(self) -> Dict[str, Any]:
        """Verifica a atualidade dos dados"""
        try:
            from sqlalchemy import func
            
            # Último registro por provedor
            provider_freshness = self.db.query(
                FocusCostData.provider_name,
                func.max(FocusCostData.billing_period_end).label('latest_date'),
                func.max(FocusCostData.created_at).label('last_ingested')
            ).group_by(FocusCostData.provider_name).all()
            
            freshness_data = {}
            current_date = date.today()
            
            for provider in provider_freshness:
                days_behind = (current_date - provider.latest_date).days if provider.latest_date else None
                hours_since_ingestion = (
                    (datetime.utcnow() - provider.last_ingested).total_seconds() / 3600
                ) if provider.last_ingested else None
                
                status = "fresh"
                if days_behind and days_behind > 2:
                    status = "stale"
                elif days_behind and days_behind > 1:
                    status = "warning"
                
                freshness_data[provider.provider_name] = {
                    "latest_data_date": provider.latest_date,
                    "last_ingested": provider.last_ingested,
                    "days_behind": days_behind,
                    "hours_since_ingestion": hours_since_ingestion,
                    "status": status
                }
            
            return {
                "providers": freshness_data,
                "checked_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error checking data freshness: {str(e)}")
            return {"error": str(e)}