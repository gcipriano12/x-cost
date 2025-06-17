"""
Response Helper Utilities

Utilitários para formatação consistente de respostas da API
"""

import time
import functools
from typing import Dict, Any, Optional, Union, List
from datetime import datetime
from fastapi import Response
from fastapi.responses import JSONResponse


def calculate_processing_time(func):
    """
    Decorator para calcular tempo de processamento de endpoints
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        processing_time = time.time() - start_time
        
        # Se o resultado é um dict, adiciona processing_time aos metadata
        if isinstance(result, dict) and 'metadata' in result:
            result['metadata']['processing_time'] = round(processing_time, 3)
        
        return result
    
    return wrapper


def generate_metadata(
    total_items: Optional[int] = None,
    processing_time: Optional[float] = None,
    additional_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Gera metadados padrão para respostas da API
    
    Args:
        total_items: Total de items na resposta
        processing_time: Tempo de processamento em segundos
        additional_info: Informações adicionais
        
    Returns:
        Dicionário com metadados
    """
    metadata = {
        "timestamp": datetime.utcnow().isoformat(),
        "api_version": "v1"
    }
    
    if total_items is not None:
        metadata["total_items"] = total_items
    
    if processing_time is not None:
        metadata["processing_time"] = round(processing_time, 3)
    
    if additional_info:
        metadata.update(additional_info)
    
    return metadata


def format_success_response(
    data: Any,
    message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    status_code: int = 200
) -> Dict[str, Any]:
    """
    Formata uma resposta de sucesso padronizada
    
    Args:
        data: Dados da resposta
        message: Mensagem opcional
        metadata: Metadados opcionais
        status_code: Código de status HTTP
        
    Returns:
        Resposta formatada
    """
    response = {
        "success": True,
        "data": data
    }
    
    if message:
        response["message"] = message
    
    if metadata:
        response["metadata"] = metadata
    else:
        response["metadata"] = generate_metadata()
    
    return response


def format_error_response(
    error: str,
    details: Optional[str] = None,
    error_code: Optional[str] = None,
    status_code: int = 400
) -> JSONResponse:
    """
    Formata uma resposta de erro padronizada
    
    Args:
        error: Mensagem de erro principal
        details: Detalhes adicionais do erro
        error_code: Código interno do erro
        status_code: Código de status HTTP
        
    Returns:
        JSONResponse com erro formatado
    """
    response_data = {
        "success": False,
        "error": error,
        "metadata": generate_metadata()
    }
    
    if details:
        response_data["details"] = details
    
    if error_code:
        response_data["error_code"] = error_code
    
    return JSONResponse(
        status_code=status_code,
        content=response_data
    )


def format_list_response(
    items: List[Any],
    total_items: Optional[int] = None,
    message: Optional[str] = None,
    additional_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Formata uma resposta com lista de items
    
    Args:
        items: Lista de items
        total_items: Total de items (se diferente do tamanho da lista)
        message: Mensagem opcional
        additional_metadata: Metadados adicionais
        
    Returns:
        Resposta formatada
    """
    if total_items is None:
        total_items = len(items)
    
    metadata = generate_metadata(
        total_items=total_items,
        additional_info=additional_metadata
    )
    
    return format_success_response(
        data=items,
        message=message,
        metadata=metadata
    )


def format_single_item_response(
    item: Any,
    message: Optional[str] = None,
    additional_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Formata uma resposta com um único item
    
    Args:
        item: Item da resposta
        message: Mensagem opcional
        additional_metadata: Metadados adicionais
        
    Returns:
        Resposta formatada
    """
    metadata = generate_metadata(additional_info=additional_metadata)
    
    return format_success_response(
        data=item,
        message=message,
        metadata=metadata
    )


def add_cache_headers(
    response: Response,
    max_age: int = 300,
    public: bool = True
) -> None:
    """
    Adiciona headers de cache à resposta
    
    Args:
        response: Objeto Response do FastAPI
        max_age: Tempo de cache em segundos
        public: Se o cache pode ser público
    """
    cache_control = f"max-age={max_age}"
    if public:
        cache_control = f"public, {cache_control}"
    else:
        cache_control = f"private, {cache_control}"
    
    response.headers["Cache-Control"] = cache_control
    response.headers["ETag"] = f'"{hash(str(response))}"'


def add_security_headers(response: Response) -> None:
    """
    Adiciona headers de segurança à resposta
    
    Args:
        response: Objeto Response do FastAPI
    """
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"


class StandardResponse:
    """Classe helper para respostas padronizadas"""
    
    @staticmethod
    def success(
        data: Any,
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Resposta de sucesso"""
        return format_success_response(data, message, metadata)
    
    @staticmethod
    def error(
        error: str,
        details: Optional[str] = None,
        error_code: Optional[str] = None,
        status_code: int = 400
    ) -> JSONResponse:
        """Resposta de erro"""
        return format_error_response(error, details, error_code, status_code)
    
    @staticmethod
    def list(
        items: List[Any],
        total_items: Optional[int] = None,
        message: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Resposta com lista"""
        return format_list_response(items, total_items, message, additional_metadata)
    
    @staticmethod
    def item(
        item: Any,
        message: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Resposta com item único"""
        return format_single_item_response(item, message, additional_metadata)