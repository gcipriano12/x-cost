#!/usr/bin/env python3
"""
Test script for the new seasonality API endpoint
"""

import asyncio
import httpx
import json
from datetime import datetime

async def test_seasonality_endpoint():
    """Test the /api/v1/analytics/seasonality endpoint"""
    
    base_url = "http://localhost:8000"
    
    # First, get a token
    async with httpx.AsyncClient() as client:
        # Login to get token
        login_data = {
            "username": "finops_admin", 
            "password": "Password123!"
        }
        
        print("🔐 Authenticating...")
        login_response = await client.post(
            f"{base_url}/api/v1/auth/login",
            json=login_data
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return
            
        token_data = login_response.json()
        token = token_data.get("access_token")
        
        if not token:
            print("❌ No access token received")
            return
            
        print("✅ Authentication successful")
        
        # Test seasonality endpoint
        headers = {"Authorization": f"Bearer {token}"}
        
        print("\n📊 Testing seasonality endpoint...")
        
        # Test 1: Current month, no filters
        print("\n🔸 Test 1: Current month analysis")
        response = await client.get(
            f"{base_url}/api/v1/analytics/seasonality",
            headers=headers,
            params={"period": "current_month"}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint working!")
            print(f"Response structure: {list(data.keys())}")
            print("📊 FULL RESPONSE:")
            import json
            print(json.dumps(data, indent=2))
            print()
            print("📈 EXTRACTED METRICS:")
            print(f"  Monthly Comparison: {data.get('monthlyComparison')}%")
            print(f"  Weekly Pattern: {data.get('weeklyPattern')}%")
            print(f"  Seasonal Progress: {data.get('seasonalProgress')}%")
            print(f"  Trend Variation: {data.get('trendVariation')}%")
            print(f"  Status: {data.get('status')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
        
        # Test 2: With provider filter
        print("\n🔸 Test 2: With AWS provider filter")
        response = await client.get(
            f"{base_url}/api/v1/analytics/seasonality",
            headers=headers,
            params={
                "period": "current_month",
                "provider_name": "AWS"
            }
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Provider filter working!")
        else:
            print(f"❌ Error with provider filter: {response.status_code}")
            print(response.text)
        
        # Test 3: Invalid parameters
        print("\n🔸 Test 3: Invalid period parameter")
        response = await client.get(
            f"{base_url}/api/v1/analytics/seasonality",
            headers=headers,
            params={"period": "invalid_period"}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 400:
            print("✅ Parameter validation working!")
        else:
            print(f"⚠️ Expected 400, got: {response.status_code}")
        
        print("\n🎉 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_seasonality_endpoint())
