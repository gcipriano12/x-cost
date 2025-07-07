"""
Test script for time_period functionality in team costs
"""
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.team_costs_service import TeamCostsService
from app.database import get_db

async def test_time_periods():
    """Test different time periods"""
    print("🧪 Testing Team Costs with different time periods...")
    
    # Get database session
    db = next(get_db())
    
    try:
        service = TeamCostsService(db)
        
        # Test different time periods
        periods = ["7d", "30d", "90d"]
        
        for period in periods:
            print(f"\n📅 Testing period: {period}")
            result = await service.get_team_costs(time_period=period)
            
            print(f"   - Success: {result.success}")
            print(f"   - Team count: {result.team_count}")
            print(f"   - Total cost: ${result.total_cost:,.2f}")
            print(f"   - Period returned: {result.period}")
            
            if result.data:
                print(f"   - Top team: {result.data[0].team_name} (${result.data[0].total_cost:,.2f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing time periods: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = asyncio.run(test_time_periods())
    sys.exit(0 if success else 1)
