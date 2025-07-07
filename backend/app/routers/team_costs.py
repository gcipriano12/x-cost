"""
Team costs API endpoints
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth_security import get_current_user
from app.schemas.team_costs import TeamCostsResponse
from app.services.team_costs_service import TeamCostsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/team-costs", tags=["team-costs"])


@router.get("", response_model=TeamCostsResponse)
async def get_team_costs(
    time_period: str = Query("30d", description="Time period (e.g., '30d', '7d', '90d', 'this-year', 'previous-year', 'custom')"),
    custom_start_date: Optional[str] = Query(None, description="Custom start date (YYYY-MM-DD) - required when time_period='custom'"),
    custom_end_date: Optional[str] = Query(None, description="Custom end date (YYYY-MM-DD) - required when time_period='custom'"),
    provider: Optional[str] = Query(None, description="Filter by cloud provider"),
    account_id: Optional[str] = Query(None, description="Filter by account ID"),
    environment: Optional[str] = Query(None, description="Filter by environment"),
    cost_center: Optional[str] = Query(None, description="Filter by cost center"),
    limit: int = Query(10, description="Maximum number of teams to return", ge=1, le=50),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Get team costs aggregated from the tags field in focus_cost_data.
    
    This endpoint extracts team information from the JSON tags field and aggregates
    costs by team. It supports various filters for more specific analysis.
    
    - **time_period**: Time period for aggregation (30d, 7d, 90d, etc.)
    - **provider**: Filter by specific cloud provider (AWS, Azure, GCP, etc.)
    - **account_id**: Filter by specific billing account
    - **environment**: Filter by environment tag (production, staging, etc.)
    - **cost_center**: Filter by cost center tag
    - **limit**: Maximum number of teams to return (1-50)
    """
    
    try:
        service = TeamCostsService(db)
        
        result = await service.get_team_costs(
            time_period=time_period,
            custom_start_date=custom_start_date,
            custom_end_date=custom_end_date,
            provider=provider,
            account_id=account_id,
            environment=environment,
            cost_center=cost_center,
            limit=limit
        )
        
        logger.info(f"Retrieved team costs for period {time_period}, found {result.team_count} teams")
        return result
        
    except ValueError as e:
        logger.error(f"Validation error in get_team_costs: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_team_costs: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving team costs")


@router.get("/{team_name}/details")
async def get_team_details(
    team_name: str,
    time_period: str = Query("30d", description="Time period (e.g., '30d', '7d', '90d')"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Get detailed cost breakdown for a specific team.
    
    Returns services and resources used by the specified team with cost details.
    
    - **team_name**: Name of the team to get details for
    - **time_period**: Time period for the analysis
    """
    
    try:
        service = TeamCostsService(db)
        
        result = await service.get_team_details(
            team_name=team_name,
            time_period=time_period
        )
        
        logger.info(f"Retrieved details for team {team_name}")
        return result
        
    except ValueError as e:
        logger.error(f"Validation error in get_team_details: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_team_details: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving team details")
