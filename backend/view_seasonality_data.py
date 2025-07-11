#!/usr/bin/env python3
"""
Test script to see actual seasonality data
"""

import asyncio
import httpx
import json
from datetime import datetime

async def view_seasonality_data():
    """View actual seasonality data"""
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # Login
        login_data = {
            "username": "finops_admin",
            "password": "Password123!"
        }
        
        print("🔐 Getting authentication token...")
        login_response = await client.post(
            f"{base_url}/api/v1/auth/login",
            json=login_data
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return
            
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        print("📊 Fetching seasonality data...")
        
        # Get seasonality data
        response = await client.get(
            f"{base_url}/api/v1/analytics/seasonality",
            headers=headers,
            params={"period": "current_month"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Seasonality API Response:")
            print("=" * 50)
            print(json.dumps(data, indent=2, default=str))
            print("=" * 50)
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    asyncio.run(view_seasonality_data())
