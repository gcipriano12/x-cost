#!/usr/bin/env python3
"""
Test cache functionality for seasonality endpoint
"""

import asyncio
import httpx
import time

async def test_cache_functionality():
    """Test if caching is working for seasonality endpoint"""
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=30) as client:
        # Login first
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
        
        print("🔄 Testing cache functionality...")
        
        # First request (should compute fresh data)
        print("\n🔸 First request (fresh data):")
        start_time = time.time()
        response1 = await client.get(
            f"{base_url}/api/v1/analytics/seasonality",
            headers=headers,
            params={"period": "current_month"}
        )
        end_time = time.time()
        
        if response1.status_code == 200:
            data1 = response1.json()
            processing_time1 = end_time - start_time
            from_cache1 = data1.get("metadata", {}).get("from_cache", False)
            
            print(f"  Status: {response1.status_code}")
            print(f"  Processing time: {processing_time1:.3f}s")
            print(f"  From cache: {from_cache1}")
            print(f"  Monthly comparison: {data1['data']['monthly_comparison']}%")
        
        # Second request immediately (should use cache)
        print("\n🔸 Second request (should be cached):")
        start_time = time.time()
        response2 = await client.get(
            f"{base_url}/api/v1/analytics/seasonality",
            headers=headers,
            params={"period": "current_month"}
        )
        end_time = time.time()
        
        if response2.status_code == 200:
            data2 = response2.json()
            processing_time2 = end_time - start_time
            from_cache2 = data2.get("metadata", {}).get("from_cache", False)
            
            print(f"  Status: {response2.status_code}")
            print(f"  Processing time: {processing_time2:.3f}s")
            print(f"  From cache: {from_cache2}")
            print(f"  Monthly comparison: {data2['data']['monthly_comparison']}%")
            
            # Verify cache effectiveness
            if from_cache2:
                print("✅ Cache is working correctly!")
                speedup = processing_time1 / processing_time2 if processing_time2 > 0 else float('inf')
                print(f"  Cache speedup: {speedup:.1f}x faster")
            else:
                print("⚠️ Cache might not be working as expected")
        
        # Test different parameters (should not use cache)
        print("\n🔸 Third request with different parameters (fresh data):")
        start_time = time.time()
        response3 = await client.get(
            f"{base_url}/api/v1/analytics/seasonality",
            headers=headers,
            params={"period": "current_month", "provider_name": "AWS"}
        )
        end_time = time.time()
        
        if response3.status_code == 200:
            data3 = response3.json()
            processing_time3 = end_time - start_time
            from_cache3 = data3.get("metadata", {}).get("from_cache", False)
            
            print(f"  Status: {response3.status_code}")
            print(f"  Processing time: {processing_time3:.3f}s")
            print(f"  From cache: {from_cache3}")
            print(f"  Monthly comparison: {data3['data']['monthly_comparison']}%")
            
            if not from_cache3:
                print("✅ Cache key differentiation working correctly!")

if __name__ == "__main__":
    asyncio.run(test_cache_functionality())
