"""
Cloud Optimization API Router

Endpoints para análise de otimização, anomalias e oportunidades de economia
"""

import logging
from datetime import datetime, date
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_database
from app.credential_models import User
from app.auth_security import get_current_active_user, security_manager
from app.cloud_native_optimization import CloudNativeOptimizationService, get_optimization_service
from app.cloud_optimization.models import (
    AnomalyType,
    SeverityLevel,
    RecommendationType,
    CloudAnomaly,
    SavingsOpportunity,
    OptimizationRecommendation
)
from app.utils.response_helpers import StandardResponse, calculate_processing_time
from app.utils.rate_limiting import rate_limit

logger = logging.getLogger(__name__)

# Criar router
router = APIRouter(prefix="/api/v1", tags=["Cloud Native Optimization"])


@router.get("/anomalies")
@rate_limit(max_requests=100, window_minutes=1)
@calculate_processing_time
async def get_anomalies(
    # Filtros básicos
    provider: Optional[str] = Query(None, description="Cloud provider (AWS, Azure, GCP, Oracle) or None for all"),
    days: Optional[int] = Query(30, description="Number of days to look back (default: 30)"),
    severity: Optional[str] = Query(None, description="Filter by severity level: high, medium, low"),
    anomaly_type: Optional[str] = Query(None, description="Filter by anomaly type: spike, trend, usage_pattern, cost_drift"),
    service_name: Optional[str] = Query(None, description="Filter by service name"),
    
    # Filtros de custo
    min_cost_impact: Optional[float] = Query(None, description="Minimum cost impact threshold"),
    max_cost_impact: Optional[float] = Query(None, description="Maximum cost impact threshold"),
    
    # Filtros de data
    date_from: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
    
    # Busca
    search: Optional[str] = Query(None, description="Search term for resource names, descriptions, etc."),
    
    # Paginação
    page: int = Query(1, description="Page number", ge=1),
    per_page: int = Query(20, description="Items per page", ge=1, le=100),
    
    # Ordenação
    sort_by: str = Query("detected_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    
    current_user: User = Depends(get_current_active_user),
    service: CloudNativeOptimizationService = Depends(get_optimization_service)
):
    """
    Retrieve cost anomalies with advanced filtering and pagination
    
    **Query Parameters:**
    - `provider`: Cloud provider to analyze (AWS, Azure, GCP, Oracle) or None for all
    - `days`: Number of days to look back for anomaly detection (default: 30, max: 365)
    - `severity`: Filter by severity level (high, medium, low)
    - `anomaly_type`: Filter by anomaly type (spike, trend, usage_pattern, cost_drift)
    - `service_name`: Filter by specific cloud service name
    - `min_cost_impact`, `max_cost_impact`: Filter by cost impact range
    - `date_from`, `date_to`: Date range filters (YYYY-MM-DD format)
    - `search`: Search term for resource names, descriptions, and other text fields
    - `page`, `per_page`: Pagination controls
    - `sort_by`, `sort_order`: Sorting options
    
    **Returns:**
    Paginated list of detected cost anomalies with severity levels, cost impact, and metadata.
    
    **Rate Limiting:** 100 requests per minute per user
    """
    try:
        # Validar severity se fornecido
        if severity and severity.lower() not in ['high', 'medium', 'low']:
            raise HTTPException(
                status_code=400, 
                detail="Invalid severity. Must be 'high', 'medium', or 'low'"
            )
        
        # Validar sort_by
        valid_sort_fields = ['detected_at', 'cost_impact', 'severity', 'service', 'resource_name', 'anomaly_type']
        if sort_by not in valid_sort_fields:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid sort_by field. Must be one of: {', '.join(valid_sort_fields)}"
            )
        
        # Validar sort_order
        if sort_order not in ['asc', 'desc']:
            raise HTTPException(
                status_code=400, 
                detail="Invalid sort_order. Must be 'asc' or 'desc'"
            )
        
        # Validar datas se fornecidas
        start_date = None
        end_date = None
        if date_from:
            try:
                start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date_from format. Use YYYY-MM-DD")
        
        if date_to:
            try:
                end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date_to format. Use YYYY-MM-DD")
        
        # Mapear provider para formato interno
        provider_name = provider.lower() if provider else None
        
        # Buscar anomalias
        anomalies = await service.get_anomalies_by_provider(provider_name=provider_name)
        
        # Aplicar filtros
        filtered_anomalies = []
        for anomaly in anomalies:
            # Filtro por severidade
            if severity and hasattr(anomaly, 'severity') and anomaly.severity.lower() != severity.lower():
                continue
            
            # Filtro por tipo de anomalia
            if anomaly_type and hasattr(anomaly, 'anomaly_type') and anomaly_type.lower() not in anomaly.anomaly_type.lower():
                continue
            
            # Filtro por nome do serviço
            if service_name and hasattr(anomaly, 'service') and service_name.lower() not in anomaly.service.lower():
                continue
            
            # Filtro por impacto de custo mínimo
            if min_cost_impact is not None and hasattr(anomaly, 'cost_impact') and anomaly.cost_impact < min_cost_impact:
                continue
            
            # Filtro por impacto de custo máximo
            if max_cost_impact is not None and hasattr(anomaly, 'cost_impact') and anomaly.cost_impact > max_cost_impact:
                continue
            
            # Filtro por data
            if start_date and hasattr(anomaly, 'detected_at'):
                anomaly_date = anomaly.detected_at.date() if hasattr(anomaly.detected_at, 'date') else anomaly.detected_at
                if anomaly_date < start_date:
                    continue
            
            if end_date and hasattr(anomaly, 'detected_at'):
                anomaly_date = anomaly.detected_at.date() if hasattr(anomaly.detected_at, 'date') else anomaly.detected_at
                if anomaly_date > end_date:
                    continue
            
            # Filtro de busca
            if search:
                search_term = search.lower()
                searchable_fields = []
                
                if hasattr(anomaly, 'resource_name'):
                    searchable_fields.append(str(anomaly.resource_name).lower())
                if hasattr(anomaly, 'description'):
                    searchable_fields.append(str(anomaly.description).lower())
                if hasattr(anomaly, 'service'):
                    searchable_fields.append(str(anomaly.service).lower())
                if hasattr(anomaly, 'anomaly_type'):
                    searchable_fields.append(str(anomaly.anomaly_type).lower())
                
                if not any(search_term in field for field in searchable_fields):
                    continue
            
            filtered_anomalies.append(anomaly)
        
        # Ordenação
        def get_sort_key(anomaly):
            if sort_by == 'detected_at':
                return getattr(anomaly, 'detected_at', datetime.min) or datetime.min
            elif sort_by == 'cost_impact':
                return getattr(anomaly, 'cost_impact', 0) or 0
            elif sort_by == 'severity':
                severity_order = {'high': 3, 'medium': 2, 'low': 1}
                return severity_order.get(getattr(anomaly, 'severity', '').lower(), 0)
            elif sort_by == 'service':
                return getattr(anomaly, 'service', '') or ''
            elif sort_by == 'resource_name':
                return getattr(anomaly, 'resource_name', '') or ''
            elif sort_by == 'anomaly_type':
                return getattr(anomaly, 'anomaly_type', '') or ''
            else:
                return getattr(anomaly, sort_by, '') or ''
        
        filtered_anomalies.sort(key=get_sort_key, reverse=(sort_order == 'desc'))
        
        # Calcular métricas totais (antes da paginação)
        total_count = len(filtered_anomalies)
        total_cost_impact = sum(getattr(a, 'cost_impact', 0) or 0 for a in filtered_anomalies)
        
        severity_count = {}
        for anomaly in filtered_anomalies:
            if hasattr(anomaly, 'severity'):
                severity_level = anomaly.severity
                severity_count[severity_level] = severity_count.get(severity_level, 0) + 1
        
        # Paginação
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        paginated_anomalies = filtered_anomalies[start_index:end_index]
        
        # Calcular total de páginas
        total_pages = (total_count + per_page - 1) // per_page
        
        logger.info(f"Retrieved {len(paginated_anomalies)} anomalies (page {page}/{total_pages}, total: {total_count}) for user {current_user.username}")
        
        return StandardResponse.success({
            "anomalies": paginated_anomalies,
            "total_count": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "total_cost_impact": round(total_cost_impact, 2),
            "severity_breakdown": severity_count,
            "filters": {
                "provider": provider,
                "days": days,
                "severity": severity,
                "anomaly_type": anomaly_type,
                "service_name": service_name,
                "min_cost_impact": min_cost_impact,
                "max_cost_impact": max_cost_impact,
                "date_from": date_from,
                "date_to": date_to,
                "search": search
            },
            "sort": {
                "sort_by": sort_by,
                "sort_order": sort_order
            },
            "requested_by": current_user.username
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get anomalies: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve anomalies")


@router.get("/savings-opportunities")
@rate_limit(max_requests=100, window_minutes=1)
@calculate_processing_time
async def get_savings_opportunities(
    # Filtros
    provider: Optional[str] = Query(None, description="Cloud provider (AWS, Azure, GCP, Oracle) or None for all"),
    min_savings: Optional[float] = Query(None, description="Minimum monthly savings threshold in USD"),
    max_savings: Optional[float] = Query(None, description="Maximum monthly savings threshold in USD"),
    category: Optional[str] = Query(None, description="Filter by category: rightsizing, unused_resources, reserved_instances, etc."),
    confidence_level: Optional[str] = Query(None, description="Filter by confidence level: high, medium, low"),
    implementation_effort: Optional[str] = Query(None, description="Filter by implementation effort: low, medium, high"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level: low, medium, high"),
    service_name: Optional[str] = Query(None, description="Filter by service name"),
    
    # Busca
    search: Optional[str] = Query(None, description="Search term for resource names, descriptions, etc."),
    
    # Paginação
    page: int = Query(1, description="Page number", ge=1),
    per_page: int = Query(20, description="Items per page", ge=1, le=100),
    
    # Ordenação
    sort_by: str = Query("potential_savings", description="Sort field: potential_savings, confidence_level, implementation_effort, risk_level"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    
    current_user: User = Depends(get_current_active_user),
    service: CloudNativeOptimizationService = Depends(get_optimization_service)
):
    """
    Retrieve savings opportunities with advanced filtering and pagination
    
    **Query Parameters:**
    - `provider`: Cloud provider to analyze (AWS, Azure, GCP, Oracle) or None for all
    - `min_savings`, `max_savings`: Filter by monthly savings range
    - `category`: Filter by savings category (rightsizing, unused_resources, reserved_instances, etc.)
    - `confidence_level`: Filter by confidence level (high, medium, low)
    - `implementation_effort`: Filter by implementation effort (low, medium, high)  
    - `risk_level`: Filter by risk level (low, medium, high)
    - `service_name`: Filter by specific cloud service name
    - `search`: Search term for resource names, descriptions, and other text fields
    - `page`, `per_page`: Pagination controls
    - `sort_by`, `sort_order`: Sorting options
    
    **Returns:**
    Paginated list of savings opportunities with estimated monthly savings, confidence levels, and implementation details.
    
    **Rate Limiting:** 100 requests per minute per user
    """
    try:
        # Mapear provider para formato interno
        provider_name = provider.lower() if provider else None
        
        # Buscar oportunidades
        opportunities = await service.get_savings_opportunities_by_provider(provider_name=provider_name)
        
        # Aplicar filtros (implementação similar ao get_anomalies)
        filtered_opportunities = []
        for opportunity in opportunities:
            # Filtro por economia mínima/máxima
            if min_savings is not None and hasattr(opportunity, 'potential_savings') and opportunity.potential_savings < min_savings:
                continue
            if max_savings is not None and hasattr(opportunity, 'potential_savings') and opportunity.potential_savings > max_savings:
                continue
            
            # Outros filtros por categoria, confidence_level, etc.
            if category and hasattr(opportunity, 'category') and category.lower() not in opportunity.category.lower():
                continue
            
            if confidence_level and hasattr(opportunity, 'confidence_level') and opportunity.confidence_level.lower() != confidence_level.lower():
                continue
            
            if implementation_effort and hasattr(opportunity, 'implementation_effort') and opportunity.implementation_effort.lower() != implementation_effort.lower():
                continue
            
            if risk_level and hasattr(opportunity, 'risk_level') and opportunity.risk_level.lower() != risk_level.lower():
                continue
            
            if service_name and hasattr(opportunity, 'service') and service_name.lower() not in opportunity.service.lower():
                continue
            
            # Filtro de busca
            if search:
                search_term = search.lower()
                searchable_fields = []
                
                if hasattr(opportunity, 'resource_name'):
                    searchable_fields.append(str(opportunity.resource_name).lower())
                if hasattr(opportunity, 'description'):
                    searchable_fields.append(str(opportunity.description).lower())
                if hasattr(opportunity, 'category'):
                    searchable_fields.append(str(opportunity.category).lower())
                
                if not any(search_term in field for field in searchable_fields):
                    continue
            
            filtered_opportunities.append(opportunity)
        
        # Ordenação
        def get_sort_key(opportunity):
            if sort_by == 'potential_savings':
                return getattr(opportunity, 'potential_savings', 0) or 0
            elif sort_by == 'confidence_level':
                confidence_order = {'high': 3, 'medium': 2, 'low': 1}
                return confidence_order.get(getattr(opportunity, 'confidence_level', '').lower(), 0)
            elif sort_by == 'implementation_effort':
                effort_order = {'low': 1, 'medium': 2, 'high': 3}
                return effort_order.get(getattr(opportunity, 'implementation_effort', '').lower(), 0)
            elif sort_by == 'risk_level':
                risk_order = {'low': 1, 'medium': 2, 'high': 3}
                return risk_order.get(getattr(opportunity, 'risk_level', '').lower(), 0)
            else:
                return getattr(opportunity, sort_by, '') or ''
        
        filtered_opportunities.sort(key=get_sort_key, reverse=(sort_order == 'desc'))
        
        # Calcular métricas totais
        total_count = len(filtered_opportunities)
        total_potential_savings = sum(getattr(o, 'potential_savings', 0) or 0 for o in filtered_opportunities)
        
        # Paginação
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        paginated_opportunities = filtered_opportunities[start_index:end_index]
        
        total_pages = (total_count + per_page - 1) // per_page
        
        logger.info(f"Retrieved {len(paginated_opportunities)} savings opportunities for user {current_user.username}")
        
        return StandardResponse.success({
            "savings_opportunities": paginated_opportunities,
            "total_count": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "total_potential_savings": round(total_potential_savings, 2),
            "filters": {
                "provider": provider,
                "min_savings": min_savings,
                "max_savings": max_savings,
                "category": category,
                "confidence_level": confidence_level,
                "implementation_effort": implementation_effort,
                "risk_level": risk_level,
                "service_name": service_name,
                "search": search
            },
            "sort": {
                "sort_by": sort_by,
                "sort_order": sort_order
            },
            "requested_by": current_user.username
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get savings opportunities: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve savings opportunities")


@router.get("/optimization/recommendations")
@calculate_processing_time
async def get_optimization_recommendations(
    provider_name: Optional[str] = Query(None, description="Cloud provider to check"),
    recommendation_type: Optional[RecommendationType] = Query(None, description="Type of recommendations to include"),
    force_refresh: bool = Query(False, description="Force refresh from cache"),
    current_user: User = Depends(get_current_active_user),
    service: CloudNativeOptimizationService = Depends(get_optimization_service)
):
    """
    Get comprehensive optimization recommendations
    
    Returns prioritized list of optimization recommendations based on anomalies and savings opportunities.
    """
    try:
        recommendations = await service.get_unified_recommendations(provider_name=provider_name)
        logger.info(f"Retrieved {len(recommendations)} recommendations for user {current_user.username}")
        return recommendations
    except Exception as e:
        logger.error(f"Failed to get recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve recommendations")


@router.get("/optimization/summary")
@rate_limit(max_requests=50, window_minutes=1)
@calculate_processing_time
async def get_optimization_summary(
    provider: Optional[str] = Query(None, description="Cloud provider (AWS, Azure, GCP, Oracle) or None for all"),
    current_user: User = Depends(get_current_active_user),
    service: CloudNativeOptimizationService = Depends(get_optimization_service)
) -> Dict[str, Any]:
    """
    Get comprehensive optimization summary
    
    **Query Parameters:**
    - `provider`: Cloud provider to analyze (AWS, Azure, GCP, Oracle) or None for all providers
    
    **Returns:**
    Aggregated statistics and metrics for anomalies, savings opportunities, and recommendations.
    Includes optimization score, total potential impact, and prioritized insights.
    
    **Rate Limiting:** 50 requests per minute per user
    """
    try:
        # Mapear provider para formato interno
        provider_name = provider.lower() if provider else None
        
        # Chamar métodos individuais e consolidar
        anomalies = await service.get_anomalies_by_provider(provider_name)
        opportunities = await service.get_savings_opportunities_by_provider(provider_name)
        recommendations = await service.get_unified_recommendations(provider_name)
        
        # Calcular métricas agregadas
        total_cost_impact = sum(a.cost_impact for a in anomalies if hasattr(a, 'cost_impact'))
        total_potential_savings = sum(o.potential_savings for o in opportunities if hasattr(o, 'potential_savings'))
        
        # Breakdown por severidade de anomalias
        anomaly_severity_breakdown = {}
        for anomaly in anomalies:
            if hasattr(anomaly, 'severity'):
                severity = anomaly.severity
                anomaly_severity_breakdown[severity] = anomaly_severity_breakdown.get(severity, 0) + 1
        
        # Breakdown por tipo de recomendação
        recommendation_type_breakdown = {}
        for rec in recommendations:
            if hasattr(rec, 'type'):
                rec_type = rec.type
                recommendation_type_breakdown[rec_type] = recommendation_type_breakdown.get(rec_type, 0) + 1
        
        # Calcular optimization score (0-100)
        optimization_score = 100
        if anomalies:
            optimization_score -= min(50, len(anomalies) * 5)  # Penalizar anomalias
        if opportunities:
            optimization_score += min(20, len(opportunities) * 2)  # Bonificar oportunidades identificadas
        optimization_score = max(0, min(100, optimization_score))
        
        # Top insights
        top_anomaly = max(anomalies, key=lambda x: getattr(x, 'cost_impact', 0)) if anomalies else None
        top_opportunity = max(opportunities, key=lambda x: getattr(x, 'potential_savings', 0)) if opportunities else None
        
        summary = {
            "anomalies": {
                "total_count": len(anomalies),
                "total_cost_impact": round(total_cost_impact, 2),
                "severity_breakdown": anomaly_severity_breakdown,
                "top_anomaly": {
                    "description": getattr(top_anomaly, 'description', None),
                    "cost_impact": getattr(top_anomaly, 'cost_impact', 0),
                    "severity": getattr(top_anomaly, 'severity', None)
                } if top_anomaly else None
            },
            "savings_opportunities": {
                "total_count": len(opportunities),
                "total_potential_savings": round(total_potential_savings, 2),
                "top_opportunity": {
                    "description": getattr(top_opportunity, 'description', None),
                    "potential_savings": getattr(top_opportunity, 'potential_savings', 0),
                    "category": getattr(top_opportunity, 'category', None)
                } if top_opportunity else None
            },
            "recommendations": {
                "total_count": len(recommendations),
                "type_breakdown": recommendation_type_breakdown,
                "high_priority_count": len([r for r in recommendations if hasattr(r, 'priority') and r.priority in ['high', 'critical']])
            },
            "optimization_metrics": {
                "optimization_score": round(optimization_score, 1),
                "total_potential_impact": round(total_cost_impact + total_potential_savings, 2),
                "health_status": "excellent" if optimization_score >= 90 else 
                               "good" if optimization_score >= 70 else 
                               "needs_attention" if optimization_score >= 50 else "critical"
            },
            "metadata": {
                "provider": provider,
                "analysis_scope": "all_providers" if not provider else f"{provider}_only",
                "requested_by": current_user.username
            }
        }
        
        logger.info(f"Generated optimization summary for user {current_user.username}")
        return StandardResponse.success(summary)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get optimization summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve optimization summary")


@router.post("/optimization/cache/invalidate")
@calculate_processing_time
async def invalidate_optimization_cache(
    pattern: str = Query("*", description="Cache pattern to invalidate"),
    current_user: User = Depends(get_current_active_user),
    service: CloudNativeOptimizationService = Depends(get_optimization_service)
):
    """
    Invalidate cache entries matching the specified pattern
    
    Useful for forcing refresh of optimization data when cloud configurations change.
    """
    try:
        # Verificar permissões de admin
        if not security_manager.check_permission(current_user.role, "system:admin"):
            raise HTTPException(
                status_code=403,
                detail="Admin privileges required to invalidate cache"
            )
        
        await service.invalidate_cache(pattern)
        logger.info(f"Cache invalidated for pattern: {pattern} by user {current_user.username}")
        
        return StandardResponse.success({
            "message": f"Cache invalidated for pattern: {pattern}",
            "pattern": pattern,
            "invalidated_by": current_user.username
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to invalidate cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to invalidate cache")


@router.get("/optimization/providers")
async def get_supported_providers():
    """Get list of supported cloud providers for optimization"""
    return StandardResponse.success({
        "providers": ["aws", "azure", "gcp", "oracle"],
        "descriptions": {
            "aws": "Amazon Web Services",
            "azure": "Microsoft Azure", 
            "gcp": "Google Cloud Platform",
            "oracle": "Oracle Cloud Infrastructure"
        }
    })


@router.get("/optimization/types")
async def get_optimization_types():
    """Get list of supported optimization types"""
    return StandardResponse.success({
        "types": list(RecommendationType),
        "descriptions": {
            RecommendationType.RIGHTSIZING: "Rightsizing recommendations for compute resources",
            RecommendationType.RESERVED_INSTANCES: "Reserved instance recommendations",
            RecommendationType.SPOT_INSTANCES: "Spot instance recommendations",
            RecommendationType.STORAGE_OPTIMIZATION: "Storage optimization recommendations",
            RecommendationType.NETWORK_OPTIMIZATION: "Network optimization recommendations",
            RecommendationType.IDLE_RESOURCES: "Idle resource identification",
            RecommendationType.SCHEDULING: "Resource scheduling optimizations"
        }
    })


# Alias para compatibilidade
optimization_router = router