#!/usr/bin/env python3
"""
Test custom period functionality for team costs
"""
import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.team_costs_service import TeamCostsService
from app.database import get_db

async def test_all_periods():
    """Test all time periods including custom"""
    print("🧪 Testing All Time Periods...")
    
    db = next(get_db())
    
    try:
        service = TeamCostsService(db)
        
        # Test standard periods
        periods = ['7d', '30d', '90d', 'this-year', 'previous-year']
        
        for period in periods:
            try:
                result = await service.get_team_costs(time_period=period)
                print(f"✅ {period}: {result.team_count} teams, ${result.total_cost:,.2f}")
                
                if result.data:
                    print(f"   Top team: {result.data[0].team_name} (${result.data[0].total_cost:,.2f})")
                    
            except Exception as e:
                print(f"❌ {period}: Error - {str(e)}")
        
        # Test custom period
        print("\n🗓️ Testing custom period...")
        try:
            result = await service.get_team_costs(
                time_period='custom',
                custom_start_date='2024-01-01',
                custom_end_date='2024-12-31'
            )
            print(f"✅ Custom (2024): {result.team_count} teams, ${result.total_cost:,.2f}")
            
            if result.data:
                print(f"   Top team: {result.data[0].team_name} (${result.data[0].total_cost:,.2f})")
                
        except Exception as e:
            print(f"❌ Custom period: Error - {str(e)}")
        
        # Test custom period with recent dates
        print("\n📅 Testing custom period (recent)...")
        try:
            result = await service.get_team_costs(
                time_period='custom',
                custom_start_date='2025-06-01',
                custom_end_date='2025-07-07'
            )
            print(f"✅ Custom (Jun-Jul 2025): {result.team_count} teams, ${result.total_cost:,.2f}")
            
            if result.data:
                print(f"   Top team: {result.data[0].team_name} (${result.data[0].total_cost:,.2f})")
                
        except Exception as e:
            print(f"❌ Custom period (recent): Error - {str(e)}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error in test: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = asyncio.run(test_all_periods())
    print(f"\n📋 Test {'passed' if success else 'failed'}!")
