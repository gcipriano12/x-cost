"""
Serviço de Análise de Sazonalidade de Custos

Implementa lógica para calcular métricas de sazonalidade:
- Comparação mensal vs histórico
- Padrões semanais
- Progresso sazonal
- Variação de tendência
"""

import logging
from datetime import datetime, timedelta, date
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from statistics import mean, stdev
import calendar

from app.models import FocusCostData
from app.schemas.seasonality import SeasonalityResponse, SeasonalityMetadata

logger = logging.getLogger(__name__)


class SeasonalityAnalyzer:
    """Analisador de sazonalidade de custos"""
    
    def __init__(self, db: Session):
        self.db = db
        self.current_date = datetime.utcnow().date()
        
    def analyze_seasonality(
        self,
        provider_name: Optional[str] = None,
        period: str = "current_month",
        team_id: Optional[str] = None
    ) -> SeasonalityResponse:
        """
        Analisa sazonalidade de custos
        
        Args:
            provider_name: Filtro por provedor (AWS, Azure, GCP)
            period: Período de análise (current_month, current_quarter)
            team_id: Filtro por equipe específica
            
        Returns:
            SeasonalityResponse com métricas calculadas
        """
        try:
            # Obter dados históricos
            historical_data = self._get_historical_data(provider_name, team_id)
            
            # Verificar se temos dados suficientes
            if len(historical_data) < 180:  # Mínimo 6 meses
                return self._generate_fallback_response("Dados históricos insuficientes")
            
            # Calcular métricas
            monthly_comparison = self._calculate_monthly_comparison(historical_data)
            weekly_pattern = self._calculate_weekly_pattern(historical_data)
            seasonal_progress = self._calculate_seasonal_progress(historical_data)
            trend_variation = self._calculate_trend_variation(historical_data)
            
            # Determinar status
            status = self._determine_status([
                monthly_comparison, weekly_pattern, 
                seasonal_progress, trend_variation
            ])
            
            # Gerar metadados
            metadata = self._generate_metadata(historical_data, period)
            
            return SeasonalityResponse(
                monthly_comparison=round(monthly_comparison, 1),
                weekly_pattern=round(weekly_pattern, 1),
                seasonal_progress=round(seasonal_progress, 1),
                trend_variation=round(trend_variation, 1),
                status=status,
                last_updated=datetime.utcnow(),
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Erro na análise de sazonalidade: {e}")
            return self._generate_fallback_response("Erro interno na análise")
    
    def _get_historical_data(
        self, 
        provider_name: Optional[str] = None,
        team_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtém dados históricos dos últimos 24 meses
        """
        # Data de início: 24 meses atrás
        start_date = self.current_date - timedelta(days=730)
        
        # Construir query base
        query = self.db.query(
            FocusCostData.billing_period_start,
            FocusCostData.billing_period_end,
            func.sum(FocusCostData.billed_cost).label('total_cost'),
            FocusCostData.service_name,
            FocusCostData.provider_name
        ).filter(
            FocusCostData.billing_period_start >= start_date
        )
        
        # Aplicar filtros opcionais
        if provider_name:
            query = query.filter(FocusCostData.provider_name == provider_name)
        
        # TODO: Implementar filtro por team_id quando tiver o campo
        # if team_id:
        #     query = query.filter(FocusCostData.team_id == team_id)
        
        # Agrupar por data
        query = query.group_by(
            FocusCostData.billing_period_start,
            FocusCostData.billing_period_end,
            FocusCostData.service_name,
            FocusCostData.provider_name
        ).order_by(FocusCostData.billing_period_start)
        
        results = query.all()
        
        # Converter para lista de dicionários
        return [
            {
                'date': row.billing_period_start,
                'end_date': row.billing_period_end,
                'cost': float(row.total_cost or 0),
                'service': row.service_name,
                'provider': row.provider_name,
                'weekday': row.billing_period_start.weekday(),
                'month': row.billing_period_start.month,
                'year': row.billing_period_start.year
            }
            for row in results
        ]
    
    def _calculate_monthly_comparison(self, data: List[Dict[str, Any]]) -> float:
        """
        Calcula comparação do mês atual com média histórica do mesmo mês
        """
        current_month = self.current_date.month
        current_year = self.current_date.year
        
        # Custos do mês atual
        current_month_costs = [
            row['cost'] for row in data 
            if row['month'] == current_month and row['year'] == current_year
        ]
        
        # Custos históricos do mesmo mês (anos anteriores)
        historical_same_month = [
            row['cost'] for row in data 
            if row['month'] == current_month and row['year'] < current_year
        ]
        
        if not current_month_costs or not historical_same_month:
            return 75.0  # Valor padrão
        
        current_avg = mean(current_month_costs)
        historical_avg = mean(historical_same_month)
        
        if historical_avg == 0:
            return 100.0
        
        # Retorna percentual: 100% = igual ao histórico
        comparison = (current_avg / historical_avg) * 100
        return min(max(comparison, 0), 100)
    
    def _calculate_weekly_pattern(self, data: List[Dict[str, Any]]) -> float:
        """
        Calcula aderência ao padrão semanal histórico
        """
        # Agrupar custos por dia da semana
        weekday_costs = {i: [] for i in range(7)}  # 0 = Segunda, 6 = Domingo
        
        for row in data:
            weekday_costs[row['weekday']].append(row['cost'])
        
        # Calcular média por dia da semana
        weekday_averages = {}
        for weekday, costs in weekday_costs.items():
            if costs:
                weekday_averages[weekday] = mean(costs)
            else:
                weekday_averages[weekday] = 0
        
        # Comparar últimas 4 semanas com padrão histórico
        last_month_data = [
            row for row in data 
            if row['date'] >= self.current_date - timedelta(days=28)
        ]
        
        if not last_month_data:
            return 85.0  # Valor padrão
        
        # Calcular variação do padrão
        recent_weekday_costs = {i: [] for i in range(7)}
        for row in last_month_data:
            recent_weekday_costs[row['weekday']].append(row['cost'])
        
        deviations = []
        for weekday in range(7):
            if recent_weekday_costs[weekday] and weekday_averages[weekday] > 0:
                recent_avg = mean(recent_weekday_costs[weekday])
                historical_avg = weekday_averages[weekday]
                deviation = abs(recent_avg - historical_avg) / historical_avg
                deviations.append(deviation)
        
        if not deviations:
            return 85.0
        
        # Converter desvio em aderência (menor desvio = maior aderência)
        avg_deviation = mean(deviations)
        adherence = max(0, 100 - (avg_deviation * 100))
        return min(adherence, 100)
    
    def _calculate_seasonal_progress(self, data: List[Dict[str, Any]]) -> float:
        """
        Calcula progresso até o pico sazonal esperado
        """
        current_month = self.current_date.month
        
        # Analisar padrão sazonal histórico
        monthly_costs = {i: [] for i in range(1, 13)}
        for row in data:
            monthly_costs[row['month']].append(row['cost'])
        
        # Calcular média por mês
        monthly_averages = {}
        for month, costs in monthly_costs.items():
            if costs:
                monthly_averages[month] = mean(costs)
            else:
                monthly_averages[month] = 0
        
        # Encontrar o mês de pico
        if not monthly_averages:
            return 50.0
        
        peak_month = max(monthly_averages.keys(), key=lambda k: monthly_averages[k])
        
        # Calcular progresso até o pico
        if peak_month == current_month:
            return 100.0
        elif peak_month > current_month:
            # Pico ainda não chegou este ano
            progress = ((current_month - 1) / (peak_month - 1)) * 100
        else:
            # Pico já passou este ano, calcular para próximo ano
            months_after_peak = 12 - peak_month
            months_until_next_peak = months_after_peak + peak_month
            months_since_peak = current_month - peak_month
            progress = (months_since_peak / months_until_next_peak) * 100
        
        return min(max(progress, 0), 100)
    
    def _calculate_trend_variation(self, data: List[Dict[str, Any]]) -> float:
        """
        Calcula variação vs tendência de longo prazo
        """
        # Agrupar dados por mês para calcular tendência
        monthly_data = {}
        for row in data:
            month_key = f"{row['year']}-{row['month']:02d}"
            if month_key not in monthly_data:
                monthly_data[month_key] = []
            monthly_data[month_key].append(row['cost'])
        
        # Calcular totais mensais
        monthly_totals = []
        for month_key in sorted(monthly_data.keys()):
            monthly_totals.append(sum(monthly_data[month_key]))
        
        if len(monthly_totals) < 6:
            return 70.0
        
        # Calcular tendência linear simples (últimos 12 meses vs 12 anteriores)
        if len(monthly_totals) >= 24:
            recent_12 = monthly_totals[-12:]
            previous_12 = monthly_totals[-24:-12]
            
            recent_avg = mean(recent_12)
            previous_avg = mean(previous_12)
            
            if previous_avg > 0:
                trend_change = (recent_avg / previous_avg) * 100
                # Normalizar para 0-100 (100 = seguindo tendência normal)
                if 80 <= trend_change <= 120:
                    return 100.0  # Tendência normal
                elif trend_change < 80:
                    return max(trend_change, 0)
                else:
                    return max(200 - trend_change, 0)
        
        return 70.0  # Valor padrão
    
    def _determine_status(self, metrics: List[float]) -> str:
        """
        Determina status baseado nas métricas
        """
        # Contar métricas fora dos ranges normais
        attention_count = sum(1 for m in metrics if 50 <= m < 70 or 130 < m <= 150)
        alert_count = sum(1 for m in metrics if m < 50 or m > 150)
        
        if alert_count > 0:
            return "alert"
        elif attention_count >= 2:
            return "attention"
        else:
            return "normal"
    
    def _generate_metadata(
        self, 
        data: List[Dict[str, Any]], 
        period: str
    ) -> SeasonalityMetadata:
        """
        Gera metadados da análise
        """
        # Calcular meses de histórico
        if data:
            oldest_date = min(row['date'] for row in data)
            months_diff = (self.current_date.year - oldest_date.year) * 12 + \
                         (self.current_date.month - oldest_date.month)
            historical_months = max(months_diff, 1)
        else:
            historical_months = 0
        
        # Determinar qualidade dos dados
        if historical_months >= 18:
            data_quality = "Good"
        elif historical_months >= 12:
            data_quality = "Fair"
        else:
            data_quality = "Poor"
        
        # Calcular próximo pico esperado (simplificado - dezembro)
        current_year = self.current_date.year
        if self.current_date.month <= 12:
            next_peak = f"{current_year}-12-15"
        else:
            next_peak = f"{current_year + 1}-12-15"
        
        return SeasonalityMetadata(
            historical_months=historical_months,
            data_quality=data_quality,
            next_peak_expected=next_peak,
            analysis_period=period,
            confidence_level=0.85 if data_quality == "high" else 0.65
        )
    
    def _generate_fallback_response(self, reason: str) -> SeasonalityResponse:
        """
        Gera resposta com dados mock quando análise falha
        """
        logger.warning(f"Usando dados fallback para sazonalidade: {reason}")
        
        return SeasonalityResponse(
            monthly_comparison=75.0,
            weekly_pattern=85.0,
            seasonal_progress=45.0,
            trend_variation=70.0,
            status="normal",
            last_updated=datetime.utcnow(),
            metadata=SeasonalityMetadata(
                historical_months=6,
                data_quality="Poor",
                next_peak_expected="2025-12-15",
                analysis_period="current_month",
                confidence_level=0.45
            )
        )
