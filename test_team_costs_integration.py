#!/usr/bin/env python3
"""
Test the complete team costs implementation - backend + frontend integration
"""
import requests
import json

def test_team_costs_endpoint():
    """Test the team costs API endpoint"""
    base_url = "http://localhost:8000"  # Adjust if backend runs on different port
    
    print("🧪 Testing Team Costs API Endpoint...")
    
    try:
        # Test basic endpoint
        response = requests.get(f"{base_url}/team-costs")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Team costs endpoint working!")
            print(f"   - Success: {data.get('success')}")
            print(f"   - Team count: {data.get('team_count')}")
            print(f"   - Total cost: ${data.get('total_cost', 0):,.2f}")
            
            if data.get('data'):
                print("   - Sample teams:")
                for team in data['data'][:3]:
                    print(f"     * {team['team_name']}: ${team['total_cost']:,.2f} ({team['percentage']:.1f}%)")
                    
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Make sure it's running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error testing endpoint: {str(e)}")
        return False

def test_with_filters():
    """Test with various filters"""
    base_url = "http://localhost:8000"
    
    print("\n🔍 Testing with filters...")
    
    # Test with different time periods
    test_cases = [
        {"time_period": "7d", "name": "Last 7 days"},
        {"time_period": "30d", "name": "Last 30 days"},
        {"time_period": "90d", "name": "Last 90 days"},
        {"limit": "5", "name": "Limit to 5 teams"}
    ]
    
    for test_case in test_cases:
        try:
            params = {k: v for k, v in test_case.items() if k != "name"}
            response = requests.get(f"{base_url}/team-costs", params=params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {test_case['name']}: {data.get('team_count', 0)} teams, ${data.get('total_cost', 0):,.2f}")
            else:
                print(f"❌ {test_case['name']}: Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ {test_case['name']}: Error - {str(e)}")

if __name__ == "__main__":
    success = test_team_costs_endpoint()
    if success:
        test_with_filters()
    
    print("\n📝 Next steps:")
    print("   1. Start the backend server: cd backend && uvicorn app.main:app --reload")
    print("   2. Start the frontend: cd frontend && npm run dev")
    print("   3. Check the dashboard for the new 'Gastos por Equipe' chart")
    print("   4. Verify that real data is being displayed instead of mock data")
