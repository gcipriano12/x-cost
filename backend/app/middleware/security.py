"""
Security Middleware

Middleware para segurança HTTP e logging de requisições
"""

import logging
from datetime import datetime
from typing import Callable
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware


logger = logging.getLogger(__name__)


async def security_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware de segurança para adicionar headers de proteção
    
    Args:
        request: Requisição HTTP
        call_next: Próximo middleware na cadeia
        
    Returns:
        Response com headers de segurança
    """
    response = await call_next(request)
    
    # Headers de segurança essenciais
    security_headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY", 
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Content-Security-Policy": "default-src 'self'",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    }
    
    for header, value in security_headers.items():
        response.headers[header] = value
    
    return response


async def request_logging_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware para logging detalhado de requisições
    
    Args:
        request: Requisição HTTP
        call_next: Próximo middleware na cadeia
        
    Returns:
        Response com logging aplicado
    """
    start_time = datetime.utcnow()
    
    # Log da requisição recebida
    logger.info(
        f"Request received: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )
    
    # Processar requisição
    response = await call_next(request)
    
    # Calcular tempo de processamento
    process_time = (datetime.utcnow() - start_time).total_seconds()
    
    # Log da resposta
    log_level = logging.WARNING if response.status_code >= 400 else logging.INFO
    logger.log(
        log_level,
        f"Request completed: {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    # Adicionar header com tempo de processamento
    response.headers["X-Process-Time"] = f"{process_time:.3f}"
    
    return response


def configure_cors_middleware(app, 
                            allow_origins: list = None,
                            allow_credentials: bool = True,
                            allow_methods: list = None,
                            allow_headers: list = None):
    """
    Configura CORS middleware com opções personalizáveis
    
    Args:
        app: Instância do FastAPI
        allow_origins: Origens permitidas (None = todas)
        allow_credentials: Permitir credenciais
        allow_methods: Métodos HTTP permitidos (None = todos)
        allow_headers: Headers permitidos (None = todos)
    """
    
    # Configurações padrão para desenvolvimento
    if allow_origins is None:
        allow_origins = ["*"]  # Configure adequadamente em produção
    
    if allow_methods is None:
        allow_methods = ["*"]
    
    if allow_headers is None:
        allow_headers = ["*"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
    )


class SecurityConfig:
    """
    Configuração de segurança centralizizada
    """
    
    # Headers de segurança padrão
    DEFAULT_SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block", 
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    
    # CSP para diferentes ambientes
    CSP_DEVELOPMENT = "default-src 'self' 'unsafe-inline' 'unsafe-eval'; img-src 'self' data: https:;"
    CSP_PRODUCTION = "default-src 'self'; img-src 'self' data: https:; script-src 'self';"
    
    @classmethod
    def get_csp_header(cls, environment: str = "development") -> str:
        """
        Retorna o CSP apropriado para o ambiente
        """
        if environment.lower() == "production":
            return cls.CSP_PRODUCTION
        return cls.CSP_DEVELOPMENT
    
    @classmethod
    def get_security_headers(cls, environment: str = "development") -> dict:
        """
        Retorna headers de segurança para o ambiente
        """
        headers = cls.DEFAULT_SECURITY_HEADERS.copy()
        headers["Content-Security-Policy"] = cls.get_csp_header(environment)
        
        if environment.lower() == "production":
            # Headers adicionais para produção
            headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return headers


def apply_security_headers(response: Response, environment: str = "development") -> None:
    """
    Aplica headers de segurança a uma resposta
    
    Args:
        response: Objeto Response do FastAPI
        environment: Ambiente (development/production)
    """
    headers = SecurityConfig.get_security_headers(environment)
    
    for header, value in headers.items():
        response.headers[header] = value


async def comprehensive_security_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware de segurança abrangente que combina multiple proteções
    
    Args:
        request: Requisição HTTP
        call_next: Próximo middleware na cadeia
        
    Returns:
        Response com todas as proteções aplicadas
    """
    start_time = datetime.utcnow()
    
    # Log da requisição
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )
    
    # Processar requisição
    response = await call_next(request)
    
    # Aplicar headers de segurança
    apply_security_headers(response)
    
    # Calcular e adicionar tempo de processamento
    process_time = (datetime.utcnow() - start_time).total_seconds()
    response.headers["X-Process-Time"] = f"{process_time:.3f}"
    
    # Log final
    log_level = logging.WARNING if response.status_code >= 400 else logging.INFO
    logger.log(
        log_level,
        f"Response: {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response