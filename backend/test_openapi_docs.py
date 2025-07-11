#!/usr/bin/env python3
"""
Test OpenAPI/Swagger documentation access
"""

import asyncio
import httpx

async def test_openapi_docs():
    """Test if OpenAPI documentation is accessible"""
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("📚 Testing OpenAPI documentation...")
        
        # Test /docs endpoint (Swagger UI)
        docs_response = await client.get(f"{base_url}/docs")
        print(f"Swagger UI (/docs): {docs_response.status_code}")
        
        # Test /openapi.json endpoint
        openapi_response = await client.get(f"{base_url}/openapi.json")
        print(f"OpenAPI JSON (/openapi.json): {openapi_response.status_code}")
        
        if openapi_response.status_code == 200:
            openapi_data = openapi_response.json()
            
            # Check if seasonality endpoint is documented
            paths = openapi_data.get("paths", {})
            seasonality_path = "/api/v1/analytics/seasonality"
            
            if seasonality_path in paths:
                print("✅ Seasonality endpoint found in OpenAPI documentation")
                endpoint_doc = paths[seasonality_path]
                
                if "get" in endpoint_doc:
                    get_doc = endpoint_doc["get"]
                    print(f"  Summary: {get_doc.get('summary', 'N/A')}")
                    print(f"  Description available: {'description' in get_doc}")
                    print(f"  Parameters documented: {len(get_doc.get('parameters', []))}")
                    print(f"  Response schemas: {len(get_doc.get('responses', {}))}")
                    
                    # Check if parameters are documented
                    parameters = get_doc.get('parameters', [])
                    for param in parameters:
                        print(f"    - {param.get('name')}: {param.get('description', 'No description')}")
            else:
                print("❌ Seasonality endpoint not found in OpenAPI documentation")
        
        print("\n🔗 Access URLs:")
        print(f"  Swagger UI: {base_url}/docs")
        print(f"  ReDoc: {base_url}/redoc")
        print(f"  OpenAPI JSON: {base_url}/openapi.json")

if __name__ == "__main__":
    asyncio.run(test_openapi_docs())
