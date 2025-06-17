"""
Date Utilities Module

Utilitários para manipulação de datas e períodos
"""

from datetime import date, datetime, timedelta
from typing import List, Tuple, Optional
from calendar import monthrange


class DatePeriodHelper:
    """
    Helper para cálculos de períodos de datas
    """
    
    @staticmethod
    def get_month_boundaries(target_date: date) -> Tuple[date, date]:
        """
        Retorna primeiro e último dia do mês
        
        Args:
            target_date: Data de referência
            
        Returns:
            Tupla com (primeiro_dia, último_dia)
        """
        first_day = target_date.replace(day=1)
        last_day_num = monthrange(target_date.year, target_date.month)[1]
        last_day = target_date.replace(day=last_day_num)
        
        return first_day, last_day
    
    @staticmethod
    def get_quarter_boundaries(target_date: date) -> Tuple[date, date]:
        """
        Retorna primeiro e último dia do trimestre
        
        Args:
            target_date: Data de referência
            
        Returns:
            Tupla com (primeiro_dia, último_dia)
        """
        quarter = (target_date.month - 1) // 3 + 1
        
        if quarter == 1:
            first_day = date(target_date.year, 1, 1)
            last_day = date(target_date.year, 3, 31)
        elif quarter == 2:
            first_day = date(target_date.year, 4, 1)
            last_day = date(target_date.year, 6, 30)
        elif quarter == 3:
            first_day = date(target_date.year, 7, 1)
            last_day = date(target_date.year, 9, 30)
        else:  # quarter == 4
            first_day = date(target_date.year, 10, 1)
            last_day = date(target_date.year, 12, 31)
        
        return first_day, last_day
    
    @staticmethod
    def get_year_boundaries(target_date: date) -> Tuple[date, date]:
        """
        Retorna primeiro e último dia do ano
        
        Args:
            target_date: Data de referência
            
        Returns:
            Tupla com (primeiro_dia, último_dia)
        """
        first_day = date(target_date.year, 1, 1)
        last_day = date(target_date.year, 12, 31)
        
        return first_day, last_day
    
    @staticmethod
    def get_previous_period(
        start_date: date,
        end_date: date,
        period_type: str = "same_length"
    ) -> Tuple[date, date]:
        """
        Calcula período anterior para comparação
        
        Args:
            start_date: Data inicial do período atual
            end_date: Data final do período atual
            period_type: Tipo de período (same_length, month, quarter, year)
            
        Returns:
            Tupla com período anterior
        """
        period_length = (end_date - start_date).days + 1
        
        if period_type == "same_length":
            prev_end = start_date - timedelta(days=1)
            prev_start = prev_end - timedelta(days=period_length - 1)
        elif period_type == "month":
            if start_date.month == 1:
                prev_month = 12
                prev_year = start_date.year - 1
            else:
                prev_month = start_date.month - 1
                prev_year = start_date.year
            
            prev_start = date(prev_year, prev_month, 1)
            prev_end = date(prev_year, prev_month, monthrange(prev_year, prev_month)[1])
        elif period_type == "quarter":
            prev_quarter_end = DatePeriodHelper.get_quarter_boundaries(start_date)[0] - timedelta(days=1)
            prev_start, prev_end = DatePeriodHelper.get_quarter_boundaries(prev_quarter_end)
        elif period_type == "year":
            prev_year = start_date.year - 1
            prev_start = date(prev_year, 1, 1)
            prev_end = date(prev_year, 12, 31)
        else:
            raise ValueError(f"Invalid period_type: {period_type}")
        
        return prev_start, prev_end
    
    @staticmethod
    def generate_date_range(
        start_date: date,
        end_date: date,
        frequency: str = "daily"
    ) -> List[date]:
        """
        Gera lista de datas entre dois pontos
        
        Args:
            start_date: Data inicial
            end_date: Data final
            frequency: Frequência (daily, weekly, monthly)
            
        Returns:
            Lista de datas
        """
        dates = []
        current_date = start_date
        
        if frequency == "daily":
            while current_date <= end_date:
                dates.append(current_date)
                current_date += timedelta(days=1)
        elif frequency == "weekly":
            while current_date <= end_date:
                dates.append(current_date)
                current_date += timedelta(weeks=1)
        elif frequency == "monthly":
            while current_date <= end_date:
                dates.append(current_date)
                # Próximo mês
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
        else:
            raise ValueError(f"Invalid frequency: {frequency}")
        
        return dates
    
    @staticmethod
    def get_period_label(start_date: date, end_date: date) -> str:
        """
        Gera label descritivo para um período
        
        Args:
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Label do período
        """
        if start_date == end_date:
            return start_date.strftime("%Y-%m-%d")
        
        # Verificar se é mês completo
        month_start, month_end = DatePeriodHelper.get_month_boundaries(start_date)
        if start_date == month_start and end_date == month_end:
            return start_date.strftime("%B %Y")
        
        # Verificar se é trimestre completo
        quarter_start, quarter_end = DatePeriodHelper.get_quarter_boundaries(start_date)
        if start_date == quarter_start and end_date == quarter_end:
            quarter = (start_date.month - 1) // 3 + 1
            return f"Q{quarter} {start_date.year}"
        
        # Verificar se é ano completo
        year_start, year_end = DatePeriodHelper.get_year_boundaries(start_date)
        if start_date == year_start and end_date == year_end:
            return str(start_date.year)
        
        # Período personalizado
        if start_date.year == end_date.year:
            if start_date.month == end_date.month:
                return f"{start_date.strftime('%b %d')} - {end_date.strftime('%d, %Y')}"
            else:
                return f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
        else:
            return f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"
    
    @staticmethod
    def get_business_days(start_date: date, end_date: date) -> int:
        """
        Calcula número de dias úteis entre duas datas
        
        Args:
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Número de dias úteis
        """
        business_days = 0
        current_date = start_date
        
        while current_date <= end_date:
            # 0 = Segunda, 6 = Domingo
            if current_date.weekday() < 5:  # Segunda a Sexta
                business_days += 1
            current_date += timedelta(days=1)
        
        return business_days
    
    @staticmethod
    def is_current_period(start_date: date, end_date: date) -> bool:
        """
        Verifica se o período inclui a data atual
        
        Args:
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            True se período é atual
        """
        today = date.today()
        return start_date <= today <= end_date
    
    @staticmethod
    def calculate_period_progress(start_date: date, end_date: date) -> float:
        """
        Calcula progresso do período atual (0.0 a 1.0)
        
        Args:
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Progresso do período (0.0 a 1.0)
        """
        today = date.today()
        
        if today < start_date:
            return 0.0
        elif today > end_date:
            return 1.0
        else:
            total_days = (end_date - start_date).days + 1
            elapsed_days = (today - start_date).days + 1
            return elapsed_days / total_days
    
    @staticmethod
    def get_month_name(month_number: int, locale: str = "en") -> str:
        """
        Retorna nome do mês
        
        Args:
            month_number: Número do mês (1-12)
            locale: Localização (en, pt)
            
        Returns:
            Nome do mês
        """
        if locale == "pt":
            months = [
                "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
            ]
        else:  # en
            months = [
                "", "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
        
        return months[month_number] if 1 <= month_number <= 12 else ""
    
    @staticmethod
    def format_period_comparison(
        current_start: date,
        current_end: date,
        previous_start: date,
        previous_end: date
    ) -> str:
        """
        Formata comparação entre períodos
        
        Args:
            current_start: Início período atual
            current_end: Fim período atual
            previous_start: Início período anterior
            previous_end: Fim período anterior
            
        Returns:
            String formatada para comparação
        """
        current_label = DatePeriodHelper.get_period_label(current_start, current_end)
        previous_label = DatePeriodHelper.get_period_label(previous_start, previous_end)
        
        return f"{current_label} vs {previous_label}"