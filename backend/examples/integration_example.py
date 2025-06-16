"""
Exemplo de integração do Cloud Native Optimization Service com FastAPI

Este arquivo demonstra como integrar o serviço de otimização com a aplicação principal.
"""

from fastapi import FastAPI, Depends, HTTPException, Query
from typing import Optional, List
import redis
import logging
from datetime import datetime

# Imports do módulo de otimização
from app.cloud_native_optimization import (
    CloudNativeOptimizationService,
    CloudAnomaly,
    SavingsOpportunity,
    OptimizationRecommendation,
    load_config_from_env,
    create_optimization_service
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# Configuração da aplicação
# ============================================================================

app = FastAPI(
    title="X-Cost Cloud Native Optimization API",
    description="API para otimização de custos em tempo real para múltiplos provedores de nuvem",
    version="1.0.0"
)

# Variáveis globais para serviços
optimization_service: Optional[CloudNativeOptimizationService] = None
redis_client: Optional[redis.Redis] = None

@app.on_event("startup")
async def startup_event():
    """Inicializar serviços na startup da aplicação"""
    global optimization_service, redis_client
    
    try:
        # Conectar ao Redis
        redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
        
        # Testar conexão Redis
        redis_client.ping()
        logger.info("Conexão Redis estabelecida")
        
        # Carregar configuração
        config = load_config_from_env()
        logger.info("Configuração carregada das variáveis de ambiente")
        
        # Criar serviço de otimização
        optimization_service = create_optimization_service(redis_client, config)
        logger.info("Cloud Native Optimization Service inicializado")
        
    except Exception as e:
        logger.error(f"Erro na inicialização: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup na shutdown da aplicação"""
    global redis_client
    
    if redis_client:
        redis_client.close()
        logger.info("Conexão Redis fechada")

# ============================================================================
# Dependency Injection
# ============================================================================

def get_optimization_service() -> CloudNativeOptimizationService:
    """Dependency para obter o serviço de otimização"""
    if optimization_service is None:
        raise HTTPException(
            status_code=503,
            detail="Serviço de otimização não disponível"
        )
    return optimization_service

# ============================================================================
# Endpoints principais
# ============================================================================

@app.get("/api/optimization/health")
async def health_check():
    """Health check do serviço de otimização"""
    try:
        # Testar Redis
        redis_client.ping()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "redis": "connected",
                "optimization": "available" if optimization_service else "unavailable"
            }
        }
    except Exception as e:
        logger.error(f"Health check falhou: {e}")
        raise HTTPException(status_code=503, detail="Serviço não disponível")

@app.get("/api/optimization/anomalies", response_model=List[CloudAnomaly])
async def get_anomalies(
    provider: Optional[str] = Query(None, description="Provedor específico (AWS, Azure, GCP, Oracle)"),
    service: CloudNativeOptimizationService = Depends(get_optimization_service)
):
    """
    Obter anomalias de custo detectadas
    
    - **provider**: Filtrar por provedor específico (opcional)
    """
    try:
        anomalies = await service.get_anomalies_by_provider(provider)
        logger.info(f"Retornadas {len(anomalies)} anomalias para {provider or 'todos os provedores'}")
        return anomalies
    
    except Exception as e:
        logger.error(f"Erro ao obter anomalias: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/optimization/savings", response_model=List[SavingsOpportunity])
async def get_savings_opportunities(
    provider: Optional[str] = Query(None, description="Provedor específico"),
    min_savings: Optional[float] = Query(None, description="Economia mínima para filtrar"),
    service: CloudNativeOptimizationService = Depends(get_optimization_service)
):
    """
    Obter oportunidades de economia identificadas
    
    - **provider**: Filtrar por provedor específico (opcional)
    - **min_savings**: Filtrar por economia mínima (opcional)
    """
    try:
        opportunities = await service.get_savings_opportunities_by_provider(provider)
        
        # Aplicar filtro de economia mínima se fornecido
        if min_savings is not None:
            opportunities = [
                opp for opp in opportunities 
                if opp.estimated_savings >= min_savings
            ]
        
        logger.info(f"Retornadas {len(opportunities)} oportunidades para {provider or 'todos os provedores'}")
        return opportunities
    
    except Exception as e:
        logger.error(f"Erro ao obter oportunidades: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/optimization/recommendations", response_model=List[OptimizationRecommendation])
async def get_recommendations(
    provider: Optional[str] = Query(None, description="Provedor específico"),
    priority: Optional[str] = Query(None, description="Filtrar por prioridade (low, medium, high, critical)"),
    service: CloudNativeOptimizationService = Depends(get_optimization_service)
):
    """
    Obter recomendações de otimização unificadas
    
    - **provider**: Filtrar por provedor específico (opcional)
    - **priority**: Filtrar por nível de prioridade (opcional)
    """
    try:
        recommendations = await service.get_unified_recommendations(provider)
        
        # Aplicar filtro de prioridade se fornecido
        if priority:
            recommendations = [
                rec for rec in recommendations 
                if rec.priority.value == priority.lower()
            ]
        
        logger.info(f"Retornadas {len(recommendations)} recomendações para {provider or 'todos os provedores'}")
        return recommendations
    
    except Exception as e:
        logger.error(f"Erro ao obter recomendações: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/optimization/report")
async def get_optimization_report(
    provider: Optional[str] = Query(None, description="Provedor específico"),
    service: CloudNativeOptimizationService = Depends(get_optimization_service)
):
    """
    Obter relatório completo de otimização com estatísticas
    
    - **provider**: Filtrar por provedor específico (opcional)
    """
    try:
        report = await service.get_full_optimization_report(provider)
        logger.info(f"Relatório gerado para {provider or 'todos os provedores'}")
        return report
    
    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Endpoints de estatísticas e resumos
# ============================================================================

@app.get("/api/optimization/summary")
async def get_optimization_summary(
    service: CloudNativeOptimizationService = Depends(get_optimization_service)
):
    """Obter resumo executivo das otimizações"""
    try:
        # Obter dados de todos os provedores
        anomalies = await service.get_anomalies_by_provider()
        opportunities = await service.get_savings_opportunities_by_provider()
        recommendations = await service.get_unified_recommendations()
        
        # Gerar estatísticas
        stats = service.get_summary_statistics(anomalies, opportunities, recommendations)
        
        # Adicionar insights executivos
        executive_summary = {
            "total_potential_savings": stats["summary"]["total_potential_savings"],
            "critical_issues": len([a for a in anomalies if a.severity.value == "critical"]),
            "high_impact_opportunities": len([o for o in opportunities if o.estimated_savings > 1000]),
            "quick_wins": len([r for r in recommendations if "baixo" in r.implementation_time.lower()]),
            "recommendations_by_category": {},
            "top_savings_opportunities": sorted(opportunities, key=lambda x: x.estimated_savings, reverse=True)[:5]
        }
        
        return {
            "executive_summary": executive_summary,
            "detailed_statistics": stats,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Erro ao gerar resumo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/optimization/providers")
async def get_available_providers():
    """Listar provedores disponíveis e seu status"""
    try:
        if not optimization_service:
            raise HTTPException(status_code=503, detail="Serviço não disponível")
        
        providers_info = []
        for provider_name in ["AWS", "Azure", "GCP", "Oracle"]:
            is_enabled = provider_name in optimization_service.providers
            providers_info.append({
                "name": provider_name,
                "enabled": is_enabled,
                "status": "available" if is_enabled else "disabled"
            })
        
        return {
            "providers": providers_info,
            "total_enabled": len(optimization_service.providers)
        }
    
    except Exception as e:
        logger.error(f"Erro ao listar provedores: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Endpoints de cache e manutenção
# ============================================================================

@app.post("/api/optimization/cache/clear")
async def clear_cache(
    provider: Optional[str] = Query(None, description="Provedor específico para limpar cache"),
    service: CloudNativeOptimizationService = Depends(get_optimization_service)
):
    """Limpar cache de otimização"""
    try:
        # Limpar cache específico ou geral
        if provider:
            # Limpar cache específico do provedor
            keys_to_delete = [
                f"cloud_optimization:anomalies:{provider}",
                f"cloud_optimization:savings:{provider}",
                f"cloud_optimization:recommendations:{provider}"
            ]
        else:
            # Limpar todo o cache de otimização
            keys_pattern = "cloud_optimization:*"
            keys_to_delete = redis_client.keys(keys_pattern)
        
        deleted_count = 0
        for key in keys_to_delete:
            if redis_client.delete(key):
                deleted_count += 1
        
        logger.info(f"Cache limpo: {deleted_count} chaves removidas")
        return {
            "message": "Cache limpo com sucesso",
            "keys_deleted": deleted_count,
            "provider": provider or "all"
        }
    
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/optimization/cache/status")
async def get_cache_status():
    """Obter status do cache"""
    try:
        # Obter informações do Redis
        redis_info = redis_client.info()
        
        # Contar chaves de otimização
        optimization_keys = redis_client.keys("cloud_optimization:*")
        
        cache_stats = {
            "redis_connected": True,
            "total_optimization_keys": len(optimization_keys),
            "memory_used": redis_info.get("used_memory_human"),
            "connected_clients": redis_info.get("connected_clients"),
            "uptime_seconds": redis_info.get("uptime_in_seconds")
        }
        
        return cache_stats
    
    except Exception as e:
        logger.error(f"Erro ao obter status do cache: {e}")
        return {
            "redis_connected": False,
            "error": str(e)
        }

# ============================================================================
# Documentação e exemplos
# ============================================================================

@app.get("/api/optimization/docs/examples")
async def get_api_examples():
    """Obter exemplos de uso da API"""
    return {
        "examples": {
            "get_aws_anomalies": {
                "url": "/api/optimization/anomalies?provider=AWS",
                "description": "Obter anomalias apenas da AWS"
            },
            "get_high_savings": {
                "url": "/api/optimization/savings?min_savings=1000",
                "description": "Obter oportunidades com economia mínima de $1000"
            },
            "get_critical_recommendations": {
                "url": "/api/optimization/recommendations?priority=critical",
                "description": "Obter apenas recomendações críticas"
            },
            "get_azure_report": {
                "url": "/api/optimization/report?provider=Azure",
                "description": "Obter relatório completo do Azure"
            }
        },
        "response_formats": {
            "anomaly": {
                "id": "aws-anomaly-001",
                "provider": "AWS",
                "service": "EC2",
                "anomaly_type": "spike",
                "severity": "high",
                "cost_impact": 500.0,
                "description": "Pico de custo detectado"
            },
            "savings_opportunity": {
                "id": "aws-savings-001",
                "provider": "AWS",
                "opportunity_type": "rightsizing",
                "estimated_savings": 200.0,
                "confidence_level": 85.0,
                "implementation_effort": "Low"
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "integration_example:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
