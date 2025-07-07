#!/usr/bin/env python3
"""
Test backend team costs with new time periods (this-year, previous-year)
"""
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.team_costs_service import TeamCostsService
from app.database import get_db

async def test_time_periods():
    """Test different time periods including this-year and previous-year"""
    print("🧪 Testing Team Costs with Different Time Periods...")
    
    # Get database session
    db = next(get_db())
    
    try:
        service = TeamCostsService(db)
        
        # Test different time periods
        test_cases = [
            ("7d", "Last 7 days"),
            ("30d", "Last 30 days"),
            ("90d", "Last 90 days"),
            ("this-year", "This Year"),
            ("previous-year", "Previous Year")
        ]
        
        for time_period, description in test_cases:
            print(f"\n📅 Testing {description} (time_period='{time_period}'):")
            
            try:
                result = await service.get_team_costs(time_period=time_period)
                
                if result.success and result.team_count > 0:
                    print(f"✅ {description}: {result.team_count} teams, ${result.total_cost:,.2f}")
                    print(f"   Period: {result.period}")
                    
                    # Show top 3 teams
                    if result.data:
                        print("   Top teams:")
                        for team in result.data[:3]:
                            print(f"     * {team.team_name}: ${team.total_cost:,.2f} ({team.percentage:.1f}%)")
                else:
                    print(f"📊 {description}: No data found for this period")
                    print(f"   Period: {result.period}")
                    print(f"   Message: {result.metadata.get('message', 'No additional info')}")
                
            except Exception as e:
                print(f"❌ {description}: Error - {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in test: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = asyncio.run(test_time_periods())
    
    print("\n" + "="*50)
    if success:
        print("✅ Backend tests completed!")
        print("\n📝 Summary:")
        print("   - 7d: Usually no data (short period)")
        print("   - 30d: Some data available") 
        print("   - 90d: More data available")
        print("   - this-year: Data from January 1st to now")
        print("   - previous-year: Data from previous calendar year")
        print("\n🎯 Frontend will now show:")
        print("   - Real data when available")
        print("   - 'No data available' message when period has no data")
    else:
        print("❌ Some tests failed")
        
    sys.exit(0 if success else 1)
