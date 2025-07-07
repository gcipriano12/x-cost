"""
Test script for team costs endpoint
"""
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.team_costs_service import TeamCostsService
from app.database import get_db

async def test_team_costs():
    """Test the team costs service"""
    print("🧪 Testing Team Costs Service...")
    
    # Get database session
    db = next(get_db())
    
    try:
        service = TeamCostsService(db)
        
        # Test with default parameters
        result = await service.get_team_costs()
        
        print(f"✅ Team costs retrieved successfully:")
        print(f"   - Success: {result.success}")
        print(f"   - Team count: {result.team_count}")
        print(f"   - Total cost: ${result.total_cost:,.2f}")
        print(f"   - Period: {result.period}")
        
        if result.data:
            print(f"   - Teams found:")
            for team in result.data[:3]:  # Show first 3 teams
                print(f"     * {team.team_name}: ${team.total_cost:,.2f} ({team.percentage:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing team costs: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = asyncio.run(test_team_costs())
    sys.exit(0 if success else 1)
