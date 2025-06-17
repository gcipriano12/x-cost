"""
Validation Utilities

Utilitários para validação consistente em toda a API
"""

from datetime import date, datetime, timedelta
from typing import List, Optional, Any
from fastapi import HTTPException


def validate_date_range(
    start_date: Optional[date], 
    end_date: Optional[date],
    max_days: int = 365
) -> None:
    """
    Valida um range de datas
    
    Args:
        start_date: Data de início
        end_date: Data de fim
        max_days: Máximo de dias permitidos no range
        
    Raises:
        HTTPException: Se o range for inválido
    """
    if start_date and end_date:
        if start_date > end_date:
            raise HTTPException(
                status_code=400,
                detail="start_date deve ser anterior ou igual a end_date"
            )
        
        # Verificar se o range não é muito grande
        delta = end_date - start_date
        if delta.days > max_days:
            raise HTTPException(
                status_code=400,
                detail=f"Range de datas não pode exceder {max_days} dias"
            )
    
    # Verificar se as datas não são futuras
    today = date.today()
    if start_date and start_date > today:
        raise HTTPException(
            status_code=400,
            detail="start_date não pode ser uma data futura"
        )
    
    if end_date and end_date > today:
        raise HTTPException(
            status_code=400,
            detail="end_date não pode ser uma data futura"
        )


def validate_sort_params(
    sort_by: Optional[str],
    sort_order: Optional[str],
    allowed_fields: List[str]
) -> None:
    """
    Valida parâmetros de ordenação
    
    Args:
        sort_by: Campo para ordenação
        sort_order: Direção da ordenação (asc/desc)
        allowed_fields: Campos permitidos para ordenação
        
    Raises:
        HTTPException: Se os parâmetros forem inválidos
    """
    if sort_by and sort_by not in allowed_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Campo '{sort_by}' não é válido para ordenação. "
                   f"Campos permitidos: {', '.join(allowed_fields)}"
        )
    
    if sort_order and sort_order.lower() not in ['asc', 'desc']:
        raise HTTPException(
            status_code=400,
            detail="sort_order deve ser 'asc' ou 'desc'"
        )


def validate_provider(provider: str, supported_providers: List[str]) -> None:
    """
    Valida se um provedor é suportado
    
    Args:
        provider: Nome do provedor
        supported_providers: Lista de provedores suportados
        
    Raises:
        HTTPException: Se o provedor não for suportado
    """
    if provider not in supported_providers:
        raise HTTPException(
            status_code=400,
            detail=f"Provedor '{provider}' não é suportado. "
                   f"Provedores disponíveis: {', '.join(supported_providers)}"
        )


def validate_numeric_range(
    value: Optional[float],
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    field_name: str = "value"
) -> None:
    """
    Valida se um valor numérico está dentro de um range
    
    Args:
        value: Valor a validar
        min_value: Valor mínimo permitido
        max_value: Valor máximo permitido
        field_name: Nome do campo para mensagens de erro
        
    Raises:
        HTTPException: Se o valor estiver fora do range
    """
    if value is None:
        return
    
    if min_value is not None and value < min_value:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} deve ser maior ou igual a {min_value}"
        )
    
    if max_value is not None and value > max_value:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} deve ser menor ou igual a {max_value}"
        )


def validate_list_items(
    items: List[Any],
    max_items: int = 100,
    field_name: str = "items"
) -> None:
    """
    Valida uma lista de items
    
    Args:
        items: Lista a validar
        max_items: Número máximo de items permitidos
        field_name: Nome do campo para mensagens de erro
        
    Raises:
        HTTPException: Se a lista for inválida
    """
    if len(items) > max_items:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} não pode ter mais de {max_items} items"
        )


def validate_string_length(
    value: Optional[str],
    min_length: int = 0,
    max_length: int = 255,
    field_name: str = "value"
) -> None:
    """
    Valida o comprimento de uma string
    
    Args:
        value: String a validar
        min_length: Comprimento mínimo
        max_length: Comprimento máximo
        field_name: Nome do campo para mensagens de erro
        
    Raises:
        HTTPException: Se o comprimento for inválido
    """
    if value is None:
        return
    
    if len(value) < min_length:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} deve ter pelo menos {min_length} caracteres"
        )
    
    if len(value) > max_length:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} não pode ter mais de {max_length} caracteres"
        )


def validate_email(email: str) -> None:
    """
    Valida formato de email
    
    Args:
        email: Email a validar
        
    Raises:
        HTTPException: Se o email for inválido
    """
    import re
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        raise HTTPException(
            status_code=400,
            detail="Formato de email inválido"
        )