"""
Virtual Tags API - X Cost
Endpoints para gerenciamento de Virtual Tags
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.database import get_database
from app.virtual_tags_models import (
    VirtualTag, VirtualTagRule, VirtualTagAllocation,
    VirtualTagCreate, VirtualTagUpdate, VirtualTagResponse,
    VirtualTagRuleCreate, VirtualTagRuleUpdate, VirtualTagRuleResponse,
    VirtualTagCategory, DateRangeFilter, AllocationResult,
    AllocationPreview, AvailableField, DashboardMetrics
)
from app.virtual_tags_engine import VirtualTagEngine
from app.virtual_tags_analytics import VirtualTagAnalytics
from app.credential_models import User
from app.auth_security import get_current_active_user

logger = logging.getLogger(__name__)

# Router para Virtual Tags
router = APIRouter(prefix="/api/v1/virtual-tags", tags=["Virtual Tags"])

@router.get("/", response_model=List[VirtualTagResponse])
async def list_virtual_tags(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[VirtualTagCategory] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Listar Virtual Tags com filtros opcionais
    """
    try:
        query = db.query(VirtualTag)
        
        # Aplicar filtros
        if category:
            query = query.filter(VirtualTag.category == category)
        
        if is_active is not None:
            query = query.filter(VirtualTag.is_active == is_active)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    VirtualTag.name.ilike(search_term),
                    VirtualTag.description.ilike(search_term)
                )
            )
        
        # Ordenar por prioridade e nome
        query = query.order_by(VirtualTag.priority.asc(), VirtualTag.name.asc())
        
        # Aplicar paginação
        virtual_tags = query.offset(skip).limit(limit).all()
        
        logger.info(f"User {current_user.username} listed {len(virtual_tags)} virtual tags")
        return virtual_tags
        
    except Exception as e:
        logger.error(f"Error listing virtual tags: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao listar Virtual Tags")

@router.post("/", response_model=VirtualTagResponse)
async def create_virtual_tag(
    virtual_tag_data: VirtualTagCreate,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Criar nova Virtual Tag com regras
    """
    try:
        # Verificar se já existe uma Virtual Tag com o mesmo nome
        existing_tag = db.query(VirtualTag).filter(
            VirtualTag.name == virtual_tag_data.name
        ).first()
        
        if existing_tag:
            raise HTTPException(
                status_code=409,
                detail=f"Virtual Tag com nome '{virtual_tag_data.name}' já existe"
            )
        
        # Criar Virtual Tag
        virtual_tag = VirtualTag(
            name=virtual_tag_data.name,
            description=virtual_tag_data.description,
            category=virtual_tag_data.category,
            is_active=virtual_tag_data.is_active,
            priority=virtual_tag_data.priority,
            default_value=virtual_tag_data.default_value,
            created_by=current_user.id
        )
        
        db.add(virtual_tag)
        db.flush()  # Para obter o ID
        
        # Criar regras
        for rule_data in virtual_tag_data.rules:
            rule = VirtualTagRule(
                virtual_tag_id=virtual_tag.id,
                name=rule_data.name,
                description=rule_data.description,
                conditions=[condition.dict() for condition in rule_data.conditions],
                action=rule_data.action.dict(),
                priority=rule_data.priority,
                logical_operator=rule_data.logical_operator,
                is_active=rule_data.is_active
            )
            db.add(rule)
        
        db.commit()
        db.refresh(virtual_tag)
        
        logger.info(f"User {current_user.username} created virtual tag: {virtual_tag.name}")
        return virtual_tag
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating virtual tag: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao criar Virtual Tag")

@router.get("/{tag_id}", response_model=VirtualTagResponse)
async def get_virtual_tag(
    tag_id: UUID,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obter Virtual Tag específica com suas regras
    """
    try:
        virtual_tag = db.query(VirtualTag).filter(
            VirtualTag.id == tag_id
        ).first()
        
        if not virtual_tag:
            raise HTTPException(
                status_code=404,
                detail=f"Virtual Tag com ID {tag_id} não encontrada"
            )
        
        logger.info(f"User {current_user.username} retrieved virtual tag: {virtual_tag.name}")
        return virtual_tag
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving virtual tag {tag_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao obter Virtual Tag")

@router.put("/{tag_id}", response_model=VirtualTagResponse)
async def update_virtual_tag(
    tag_id: UUID,
    virtual_tag_data: VirtualTagUpdate,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Atualizar Virtual Tag existente
    """
    try:
        virtual_tag = db.query(VirtualTag).filter(
            VirtualTag.id == tag_id
        ).first()
        
        if not virtual_tag:
            raise HTTPException(
                status_code=404,
                detail=f"Virtual Tag com ID {tag_id} não encontrada"
            )
        
        # Verificar se nome já existe (se foi alterado)
        if virtual_tag_data.name and virtual_tag_data.name != virtual_tag.name:
            existing_tag = db.query(VirtualTag).filter(
                and_(
                    VirtualTag.name == virtual_tag_data.name,
                    VirtualTag.id != tag_id
                )
            ).first()
            
            if existing_tag:
                raise HTTPException(
                    status_code=409,
                    detail=f"Virtual Tag com nome '{virtual_tag_data.name}' já existe"
                )
        
        # Atualizar campos
        update_data = virtual_tag_data.dict(exclude_unset=True)
        rules_data = update_data.pop('rules', None)
        
        for field, value in update_data.items():
            setattr(virtual_tag, field, value)
        
        # Atualizar regras se fornecidas
        if rules_data is not None:
            # Remover regras existentes
            db.query(VirtualTagRule).filter(
                VirtualTagRule.virtual_tag_id == tag_id
            ).delete()
            
            # Criar novas regras
            for rule_data in rules_data:
                rule = VirtualTagRule(
                    virtual_tag_id=tag_id,
                    name=rule_data.name,
                    description=rule_data.description,
                    conditions=[condition.dict() for condition in rule_data.conditions],
                    action=rule_data.action.dict(),
                    priority=rule_data.priority,
                    logical_operator=rule_data.logical_operator,
                    is_active=rule_data.is_active
                )
                db.add(rule)
        
        virtual_tag.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(virtual_tag)
        
        logger.info(f"User {current_user.username} updated virtual tag: {virtual_tag.name}")
        return virtual_tag
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating virtual tag {tag_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao atualizar Virtual Tag")

@router.delete("/{tag_id}")
async def delete_virtual_tag(
    tag_id: UUID,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Excluir Virtual Tag e suas alocações
    """
    try:
        virtual_tag = db.query(VirtualTag).filter(
            VirtualTag.id == tag_id
        ).first()
        
        if not virtual_tag:
            raise HTTPException(
                status_code=404,
                detail=f"Virtual Tag com ID {tag_id} não encontrada"
            )
        
        tag_name = virtual_tag.name
        
        # Remover alocações
        db.query(VirtualTagAllocation).filter(
            VirtualTagAllocation.virtual_tag_id == tag_id
        ).delete()
        
        # Remover regras (cascade deve fazer isso automaticamente)
        db.query(VirtualTagRule).filter(
            VirtualTagRule.virtual_tag_id == tag_id
        ).delete()
        
        # Remover Virtual Tag
        db.delete(virtual_tag)
        db.commit()
        
        logger.info(f"User {current_user.username} deleted virtual tag: {tag_name}")
        return {"message": f"Virtual Tag '{tag_name}' excluída com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting virtual tag {tag_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao excluir Virtual Tag")

@router.post("/{tag_id}/preview", response_model=List[AllocationPreview])
async def preview_allocation(
    tag_id: UUID,
    date_range: DateRangeFilter,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Gerar preview de alocação para uma Virtual Tag
    """
    try:
        virtual_tag = db.query(VirtualTag).filter(
            VirtualTag.id == tag_id
        ).first()
        
        if not virtual_tag:
            raise HTTPException(
                status_code=404,
                detail=f"Virtual Tag com ID {tag_id} não encontrada"
            )
        
        engine = VirtualTagEngine(db)
        previews = await engine.get_allocation_preview(
            virtual_tag, date_range, limit
        )
        
        logger.info(f"User {current_user.username} generated preview for virtual tag: {virtual_tag.name}")
        return previews
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating preview for virtual tag {tag_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao gerar preview")

@router.get("/fields/available", response_model=List[AvailableField])
async def get_available_fields(
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obter campos disponíveis para criação de regras
    """
    try:
        engine = VirtualTagEngine(db)
        fields = await engine.get_available_fields()
        
        logger.info(f"User {current_user.username} retrieved available fields")
        return fields
        
    except Exception as e:
        logger.error(f"Error getting available fields: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao obter campos disponíveis")

@router.get("/metrics/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obter métricas consolidadas para dashboard
    """
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        date_range = DateRangeFilter(
            start_date=start_date,
            end_date=end_date
        )
        
        analytics = VirtualTagAnalytics(db)
        metrics = await analytics.get_dashboard_metrics(date_range)
        
        logger.info(f"User {current_user.username} retrieved dashboard metrics")
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao obter métricas")

@router.post("/process-allocation", response_model=AllocationResult)
async def process_allocation(
    date_range: DateRangeFilter,
    tag_ids: Optional[List[UUID]] = None,
    force_reprocess: bool = False,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Processar alocação de custos para período especificado
    """
    try:
        # Validar período
        if date_range.end_date < date_range.start_date:
            raise HTTPException(
                status_code=400,
                detail="Data final deve ser posterior à data inicial"
            )
        
        # Validar período máximo (1 ano)
        max_days = 365
        period_days = (date_range.end_date - date_range.start_date).days
        if period_days > max_days:
            raise HTTPException(
                status_code=400,
                detail=f"Período máximo permitido é {max_days} dias"
            )
        
        # Obter Virtual Tags para processar
        virtual_tags = None
        if tag_ids:
            virtual_tags = db.query(VirtualTag).filter(
                and_(
                    VirtualTag.id.in_(tag_ids),
                    VirtualTag.is_active == True
                )
            ).all()
            
            if len(virtual_tags) != len(tag_ids):
                raise HTTPException(
                    status_code=404,
                    detail="Uma ou mais Virtual Tags não foram encontradas"
                )
        
        # Processar alocação
        engine = VirtualTagEngine(db)
        result = await engine.process_allocation(
            date_range=date_range,
            virtual_tags=virtual_tags,
            force_reprocess=force_reprocess
        )
        
        logger.info(f"User {current_user.username} processed allocation for period {date_range.start_date} to {date_range.end_date}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing allocation: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar alocação")

@router.get("/categories/", response_model=List[str])
async def get_categories(
    current_user: User = Depends(get_current_active_user)
):
    """
    Obter categorias disponíveis para Virtual Tags
    """
    try:
        categories = [category.value for category in VirtualTagCategory]
        return categories
        
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao obter categorias")

@router.get("/{tag_id}/allocations/")
async def get_tag_allocations(
    tag_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obter alocações de uma Virtual Tag específica
    """
    try:
        virtual_tag = db.query(VirtualTag).filter(
            VirtualTag.id == tag_id
        ).first()
        
        if not virtual_tag:
            raise HTTPException(
                status_code=404,
                detail=f"Virtual Tag com ID {tag_id} não encontrada"
            )
        
        query = db.query(VirtualTagAllocation).filter(
            VirtualTagAllocation.virtual_tag_id == tag_id
        )
        
        # Aplicar filtros de data
        if start_date:
            query = query.filter(VirtualTagAllocation.allocation_date >= start_date)
        
        if end_date:
            query = query.filter(VirtualTagAllocation.allocation_date <= end_date)
        
        # Ordenar por data mais recente
        query = query.order_by(VirtualTagAllocation.allocation_date.desc())
        
        # Aplicar paginação
        allocations = query.offset(skip).limit(limit).all()
        
        # Converter para response format
        allocation_list = []
        for allocation in allocations:
            allocation_list.append({
                'id': str(allocation.id),
                'cost_record_id': allocation.cost_record_id,
                'tag_value': allocation.tag_value,
                'allocated_cost': float(allocation.allocated_cost),
                'allocation_percentage': float(allocation.allocation_percentage),
                'allocation_date': allocation.allocation_date.isoformat(),
                'processed_at': allocation.processed_at.isoformat()
            })
        
        logger.info(f"User {current_user.username} retrieved {len(allocations)} allocations for virtual tag: {virtual_tag.name}")
        return {
            'virtual_tag_name': virtual_tag.name,
            'total_allocations': len(allocation_list),
            'allocations': allocation_list
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting allocations for virtual tag {tag_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao obter alocações")
