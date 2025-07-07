"""
Schemas for team costs API endpoints
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class TeamCostItem(BaseModel):
    """Individual team cost item"""
    team_name: str = Field(..., description="Name of the team")
    total_cost: float = Field(..., description="Total cost for the team")
    percentage: float = Field(..., description="Percentage of total costs")
    resource_count: int = Field(..., description="Number of resources for this team")
    avg_cost_per_resource: float = Field(..., description="Average cost per resource")
    color: str = Field(..., description="Color for chart visualization")


class TeamCostsResponse(BaseModel):
    """Response model for team costs endpoint"""
    success: bool = Field(True, description="Whether the request was successful")
    data: List[TeamCostItem] = Field(..., description="List of team cost items")
    total_cost: float = Field(..., description="Total cost across all teams")
    period: str = Field(..., description="Time period for the data")
    team_count: int = Field(..., description="Total number of teams")
    last_updated: datetime = Field(..., description="When the data was last updated")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class TeamCostsRequest(BaseModel):
    """Request parameters for team costs"""
    time_period: str = Field("30d", description="Time period (e.g., '30d', '7d', '90d')")
    provider: Optional[str] = Field(None, description="Filter by cloud provider")
    account_id: Optional[str] = Field(None, description="Filter by account ID")
    environment: Optional[str] = Field(None, description="Filter by environment")
    cost_center: Optional[str] = Field(None, description="Filter by cost center")
    limit: int = Field(10, description="Maximum number of teams to return")
