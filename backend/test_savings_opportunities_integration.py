#!/usr/bin/env python3
"""
Teste completo dos endpoints de Savings Opportunities
Valida os novos parâmetros, bulk actions e implementation plans
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def get_auth_token():
    """Get authentication token for testing"""
    login_data = {
        "username": "test@example.com",
        "password": "testpassword"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print("Failed to get auth token, using mock")
        return "mock_token"

def test_savings_opportunities_filters():
    """Test savings opportunities with all filter parameters"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔍 Testing Savings Opportunities Filters...")
    
    # Test cases with different filter combinations
    test_cases = [
        {
            "name": "All opportunities",
            "params": {}
        },
        {
            "name": "AWS provider with high confidence",
            "params": {
                "provider": "aws",
                "confidence_level": "high"
            }
        },
        {
            "name": "Savings range filter",
            "params": {
                "min_savings": 100,
                "max_savings": 5000
            }
        },
        {
            "name": "Low effort, low risk opportunities",
            "params": {
                "implementation_effort": "low",
                "risk_level": "low"
            }
        },
        {
            "name": "Search with pagination",
            "params": {
                "search": "instance",
                "page": 1,
                "per_page": 10
            }
        },
        {
            "name": "Sort by confidence desc",
            "params": {
                "sort_by": "confidence",
                "sort_order": "desc"
            }
        },
        {
            "name": "Combined filters",
            "params": {
                "provider": "azure",
                "category": "rightsizing",
                "confidence_level": "medium",
                "implementation_effort": "low",
                "min_savings": 50,
                "sort_by": "monthly_savings",
                "sort_order": "desc"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n  📊 {test_case['name']}")
        
        response = requests.get(
            f"{BASE_URL}/api/v1/savings-opportunities",
            params=test_case['params'],
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"    ✅ Status: {response.status_code}")
            print(f"    📈 Total opportunities: {data.get('total_count', 0)}")
            print(f"    💰 Total potential savings: ${data.get('total_potential_savings', 0):,.2f}")
            print(f"    📄 Page: {data.get('page', 1)}/{data.get('total_pages', 1)}")
            
            # Print breakdowns if available
            if 'category_breakdown' in data:
                print(f"    📊 Categories: {data['category_breakdown']}")
            if 'confidence_breakdown' in data:
                print(f"    🎯 Confidence: {data['confidence_breakdown']}")
            if 'effort_breakdown' in data:
                print(f"    💪 Effort: {data['effort_breakdown']}")
            if 'risk_breakdown' in data:
                print(f"    ⚠️  Risk: {data['risk_breakdown']}")
        else:
            print(f"    ❌ Status: {response.status_code}")
            print(f"    Error: {response.text}")
        
        time.sleep(0.5)  # Rate limiting

def test_bulk_actions():
    """Test bulk actions on savings opportunities"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print("\n🚀 Testing Bulk Actions...")
    
    # Test cases for bulk actions
    test_cases = [
        {
            "name": "Add to plan",
            "data": {
                "action": "add_to_plan",
                "opportunity_ids": ["opp_001", "opp_002", "opp_003"],
                "plan_id": "plan_001",
                "notes": "High priority items for Q1"
            }
        },
        {
            "name": "Mark as implementing",
            "data": {
                "action": "implement",
                "opportunity_ids": ["opp_004", "opp_005"],
                "notes": "Started implementation"
            }
        },
        {
            "name": "Dismiss opportunities",
            "data": {
                "action": "dismiss",
                "opportunity_ids": ["opp_006"],
                "notes": "Not applicable for current environment"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n  🎯 {test_case['name']}")
        
        response = requests.post(
            f"{BASE_URL}/api/v1/savings-opportunities/bulk-action",
            json=test_case['data'],
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"    ✅ Status: {response.status_code}")
            print(f"    📊 Action: {data.get('action')}")
            print(f"    📈 Total processed: {data.get('total_opportunities', 0)}")
            print(f"    ✅ Successful: {data.get('successful', 0)}")
            print(f"    ❌ Failed: {data.get('failed', 0)}")
        else:
            print(f"    ❌ Status: {response.status_code}")
            print(f"    Error: {response.text}")
        
        time.sleep(0.5)

def test_implementation_plans():
    """Test implementation plans endpoints"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print("\n📋 Testing Implementation Plans...")
    
    # Test getting plans
    print(f"\n  📊 Getting implementation plans")
    response = requests.get(
        f"{BASE_URL}/api/v1/implementation-plans",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"    ✅ Status: {response.status_code}")
        print(f"    📈 Total plans: {data.get('total_count', 0)}")
        print(f"    📄 Page: {data.get('page', 1)}/{data.get('total_pages', 1)}")
        
        for plan in data.get('plans', []):
            print(f"    📋 Plan: {plan['name']} ({plan['status']})")
    else:
        print(f"    ❌ Status: {response.status_code}")
        print(f"    Error: {response.text}")
    
    # Test creating a plan
    print(f"\n  ➕ Creating new implementation plan")
    plan_data = {
        "name": f"Test Plan {int(time.time())}",
        "description": "Automated test plan for cost optimization",
        "opportunity_ids": ["opp_001", "opp_002"],
        "timeline_months": 3,
        "risk_assessment": "medium"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/implementation-plans",
        json=plan_data,
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"    ✅ Status: {response.status_code}")
        print(f"    📋 Created plan: {data['plan']['name']}")
        print(f"    🆔 Plan ID: {data['plan']['id']}")
        print(f"    📅 Timeline: {data['plan']['timeline_months']} months")
    else:
        print(f"    ❌ Status: {response.status_code}")
        print(f"    Error: {response.text}")

def test_error_handling():
    """Test error handling and validation"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print("\n⚠️  Testing Error Handling...")
    
    # Test invalid parameters
    error_tests = [
        {
            "name": "Invalid sort_by field",
            "url": f"{BASE_URL}/api/v1/savings-opportunities",
            "params": {"sort_by": "invalid_field"},
            "method": "GET"
        },
        {
            "name": "Invalid confidence_level",
            "url": f"{BASE_URL}/api/v1/savings-opportunities",
            "params": {"confidence_level": "invalid"},
            "method": "GET"
        },
        {
            "name": "Invalid min/max savings range",
            "url": f"{BASE_URL}/api/v1/savings-opportunities",
            "params": {"min_savings": 1000, "max_savings": 500},
            "method": "GET"
        },
        {
            "name": "Empty bulk action",
            "url": f"{BASE_URL}/api/v1/savings-opportunities/bulk-action",
            "data": {"action": "add_to_plan", "opportunity_ids": []},
            "method": "POST"
        },
        {
            "name": "Missing plan_id for add_to_plan",
            "url": f"{BASE_URL}/api/v1/savings-opportunities/bulk-action",
            "data": {"action": "add_to_plan", "opportunity_ids": ["opp_001"]},
            "method": "POST"
        }
    ]
    
    for test in error_tests:
        print(f"\n  🔍 {test['name']}")
        
        if test['method'] == 'GET':
            response = requests.get(test['url'], params=test.get('params'), headers=headers)
        else:
            response = requests.post(test['url'], json=test.get('data'), headers=headers)
        
        if response.status_code >= 400:
            print(f"    ✅ Correctly returned error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"    📝 Error message: {error_data.get('detail', 'No detail')}")
            except:
                print(f"    📝 Error text: {response.text}")
        else:
            print(f"    ❌ Expected error but got: {response.status_code}")

def test_performance():
    """Test performance with larger datasets"""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n⚡ Testing Performance...")
    
    performance_tests = [
        {
            "name": "Large page size",
            "params": {"per_page": 100}
        },
        {
            "name": "Complex filter combination",
            "params": {
                "provider": "aws",
                "min_savings": 100,
                "confidence_level": "high",
                "implementation_effort": "low",
                "search": "compute",
                "sort_by": "monthly_savings",
                "sort_order": "desc"
            }
        },
        {
            "name": "Multiple rapid requests",
            "params": {"page": 1, "per_page": 20}
        }
    ]
    
    for test in performance_tests:
        print(f"\n  ⏱️  {test['name']}")
        
        start_time = time.time()
        
        if test['name'] == "Multiple rapid requests":
            # Test 5 rapid requests
            for i in range(5):
                response = requests.get(
                    f"{BASE_URL}/api/v1/savings-opportunities",
                    params=test['params'],
                    headers=headers
                )
        else:
            response = requests.get(
                f"{BASE_URL}/api/v1/savings-opportunities",
                params=test['params'],
                headers=headers
            )
        
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            processing_time = data.get('metadata', {}).get('processing_time_seconds', 0)
            request_time = end_time - start_time
            
            print(f"    ✅ Status: {response.status_code}")
            print(f"    ⏱️  Request time: {request_time:.3f}s")
            print(f"    🔧 Processing time: {processing_time:.3f}s")
            print(f"    📊 Results: {data.get('total_count', 0)}")
        else:
            print(f"    ❌ Status: {response.status_code}")

def main():
    """Run all tests"""
    print("🧪 Starting Savings Opportunities Integration Tests")
    print("=" * 60)
    
    try:
        test_savings_opportunities_filters()
        test_bulk_actions() 
        test_implementation_plans()
        test_error_handling()
        test_performance()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
