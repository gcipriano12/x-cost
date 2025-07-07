"""
Service layer for team costs functionality
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text, func
import json

from app.database import get_db
from app.schemas.team_costs import TeamCostItem, TeamCostsResponse

logger = logging.getLogger(__name__)


class TeamCostsService:
    """Service for handling team costs operations"""
    
    # Default colors for teams (cycling through these)
    TEAM_COLORS = [
        "#3B82F6",  # Blue
        "#10B981",  # Green  
        "#F59E0B",  # Amber
        "#EF4444",  # Red
        "#8B5CF6",  # Purple
        "#F97316",  # Orange
        "#06B6D4",  # Cyan
        "#84CC16",  # Lime
        "#EC4899",  # Pink
        "#6B7280",  # Gray
    ]
    
    def __init__(self, db: Session):
        self.db = db
    
    def _parse_time_period(self, time_period: str) -> int:
        """Parse time period string to number of days"""
        if time_period == 'custom':
            # For custom periods, return 0 as days won't be used
            return 0
        elif time_period.endswith('d'):
            return int(time_period[:-1])
        elif time_period.endswith('w'):
            return int(time_period[:-1]) * 7
        elif time_period.endswith('m'):
            return int(time_period[:-1]) * 30
        elif time_period == 'this-year':
            # Calcular dias desde o início do ano atual
            current_year = datetime.now().year
            start_of_year = datetime(current_year, 1, 1)
            days_since_start = (datetime.now() - start_of_year).days + 1
            return days_since_start
        elif time_period == 'previous-year':
            # Um ano completo (365 dias) + dias do ano atual para cobrir o ano anterior completo
            current_year = datetime.now().year
            start_of_previous_year = datetime(current_year - 1, 1, 1)
            end_of_previous_year = datetime(current_year - 1, 12, 31)
            days_in_previous_year = (end_of_previous_year - start_of_previous_year).days + 1
            
            # Adicionar dias do ano atual para garantir que pegamos o ano anterior completo
            days_current_year = (datetime.now() - datetime(current_year, 1, 1)).days + 1
            return days_in_previous_year + days_current_year
        else:
            logger.warning(f"Could not parse time_period '{time_period}', using 30 days as fallback")
            return 30  # default to 30 days
    
    def _get_team_costs_query(
        self, 
        time_period: str,
        days: int,
        custom_start_date: Optional[str] = None,
        custom_end_date: Optional[str] = None,
        provider: Optional[str] = None,
        account_id: Optional[str] = None,
        environment: Optional[str] = None,
        cost_center: Optional[str] = None,
        limit: int = 10
    ) -> str:
        """Build the SQL query for team costs"""
        
        # Determinar a condição de data baseada no time_period
        if time_period == 'custom' and custom_start_date and custom_end_date:
            date_condition = f"billing_period_start >= '{custom_start_date}' AND billing_period_start <= '{custom_end_date}'"
        elif time_period == 'this-year':
            date_condition = "EXTRACT(YEAR FROM billing_period_start) = EXTRACT(YEAR FROM CURRENT_DATE)"
        elif time_period == 'previous-year':
            date_condition = "EXTRACT(YEAR FROM billing_period_start) = EXTRACT(YEAR FROM CURRENT_DATE) - 1"
        else:
            date_condition = f"billing_period_start >= CURRENT_DATE - INTERVAL '{days} days'"
        
        base_query = f"""
        WITH team_costs AS (
            SELECT 
                COALESCE(
                    NULLIF(tags->>'team', 'null'),
                    NULLIF(tags->>'Team', 'null'),
                    'Unassigned'
                ) as team_name,
                SUM(CAST(billed_cost AS DECIMAL(15,2))) as total_cost,
                COUNT(DISTINCT resource_id) as resource_count,
                AVG(CAST(billed_cost AS DECIMAL(15,2))) as avg_cost_per_resource
            FROM finops.focus_cost_data 
            WHERE {date_condition}
                AND tags IS NOT NULL
                AND billed_cost > 0
        """
        
        # Add provider filter
        if provider:
            base_query += " AND provider_name = :provider"
        
        # Add account filter
        if account_id:
            base_query += " AND billing_account_id = :account_id"
        
        # Add environment filter
        if environment:
            base_query += " AND tags->>'environment' = :environment"
        
        # Add cost center filter  
        if cost_center:
            base_query += " AND tags->>'cost-center' = :cost_center"
        
        base_query += """
            GROUP BY 
                COALESCE(
                    NULLIF(tags->>'team', 'null'),
                    NULLIF(tags->>'Team', 'null'),
                    'Unassigned'
                )
            HAVING SUM(CAST(billed_cost AS DECIMAL(15,2))) > 0
        ),
        total_cost AS (
            SELECT SUM(total_cost) as grand_total FROM team_costs
        )
        SELECT 
            tc.team_name,
            tc.total_cost,
            ROUND((tc.total_cost / tt.grand_total) * 100, 2) as percentage,
            tc.resource_count,
            tc.avg_cost_per_resource,
            tt.grand_total
        FROM team_costs tc
        CROSS JOIN total_cost tt
        ORDER BY tc.total_cost DESC
        LIMIT :limit;
        """
        
        return base_query
    
    async def get_team_costs(
        self,
        time_period: str = "30d",
        custom_start_date: Optional[str] = None,
        custom_end_date: Optional[str] = None,
        provider: Optional[str] = None,
        account_id: Optional[str] = None,
        environment: Optional[str] = None,
        cost_center: Optional[str] = None,
        limit: int = 10
    ) -> TeamCostsResponse:
        """Get team costs data"""
        
        try:
            # Validate custom period parameters
            if time_period == 'custom':
                if not custom_start_date or not custom_end_date:
                    raise ValueError("custom_start_date and custom_end_date are required when time_period='custom'")
                
                # Validate date format
                try:
                    datetime.strptime(custom_start_date, '%Y-%m-%d')
                    datetime.strptime(custom_end_date, '%Y-%m-%d')
                except ValueError:
                    raise ValueError("Date format must be YYYY-MM-DD")
            
            days = self._parse_time_period(time_period)
            
            # Build query parameters
            params = {
                'days': days,
                'limit': limit
            }
            
            if provider:
                params['provider'] = provider
            if account_id:
                params['account_id'] = account_id
            if environment:
                params['environment'] = environment
            if cost_center:
                params['cost_center'] = cost_center
            
            # Execute query
            query = self._get_team_costs_query(
                time_period, days, custom_start_date, custom_end_date, provider, account_id, environment, cost_center, limit
            )
            
            result = self.db.execute(text(query), params)
            rows = result.fetchall()
            
            if not rows:
                # Return empty response if no data
                return TeamCostsResponse(
                    data=[],
                    total_cost=0.0,
                    period=time_period,
                    team_count=0,
                    last_updated=datetime.now(),
                    metadata={"message": "No team cost data found for the specified period"}
                )
            
            # Process results
            team_items = []
            total_cost = float(rows[0].grand_total) if rows else 0.0
            
            for i, row in enumerate(rows):
                # Assign color cycling through available colors
                color = self.TEAM_COLORS[i % len(self.TEAM_COLORS)]
                
                team_item = TeamCostItem(
                    team_name=str(row.team_name).strip(' "'),  # Clean up team name
                    total_cost=float(row.total_cost),
                    percentage=float(row.percentage),
                    resource_count=int(row.resource_count),
                    avg_cost_per_resource=float(row.avg_cost_per_resource or 0),
                    color=color
                )
                team_items.append(team_item)
            
            # Build metadata
            metadata = {
                "query_params": {
                    "time_period": time_period,
                    "provider": provider,
                    "account_id": account_id,
                    "environment": environment,
                    "cost_center": cost_center
                },
                "data_source": "finops.focus_cost_data",
                "aggregation_method": "json_extract_team_tags"
            }
            
            return TeamCostsResponse(
                data=team_items,
                total_cost=total_cost,
                period=time_period,
                team_count=len(team_items),
                last_updated=datetime.now(),
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error getting team costs: {str(e)}")
            raise ValueError(f"Failed to retrieve team costs: {str(e)}")
    
    async def get_team_details(self, team_name: str, time_period: str = "30d") -> Dict[str, Any]:
        """Get detailed information for a specific team"""
        
        try:
            days = self._parse_time_period(time_period)
            
            query = """
            SELECT 
                provider,
                service_name,
                SUM(CAST(cost AS DECIMAL(15,2))) as service_cost,
                COUNT(DISTINCT resource_id) as resource_count
            FROM finops.focus_cost_data 
            WHERE usage_date >= DATE_SUB(NOW(), INTERVAL :days DAY)
                AND JSON_EXTRACT(tags, '$.team') = :team_name
                AND cost > 0
            GROUP BY provider, service_name
            ORDER BY service_cost DESC;
            """
            
            result = self.db.execute(text(query), {
                'days': days,
                'team_name': team_name
            })
            
            services = []
            for row in result.fetchall():
                services.append({
                    'provider': row.provider,
                    'service_name': row.service_name,
                    'cost': float(row.service_cost),
                    'resource_count': int(row.resource_count)
                })
            
            return {
                'team_name': team_name,
                'period': time_period,
                'services': services,
                'total_services': len(services)
            }
            
        except Exception as e:
            logger.error(f"Error getting team details for {team_name}: {str(e)}")
            raise ValueError(f"Failed to retrieve team details: {str(e)}")


def get_team_costs_service(db: Session = None) -> TeamCostsService:
    """Factory function to create TeamCostsService instance"""
    if db is None:
        db = next(get_db())
    return TeamCostsService(db)
