// Script de teste para verificar API Oracle Cloud
// Execute no console do navegador quando estiver logado

const testOracleCloudAPI = async () => {
  const baseURL = 'http://localhost:8000';
  const token = localStorage.getItem('access_token');
  
  console.log('🧪 Testing Oracle Cloud API integration...');
  console.log('🔑 Token available:', !!token);
  
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
  
  try {
    // Test 1: Dashboard summary without filter (should show all providers)
    console.log('\n📊 Test 1: Dashboard summary without provider filter');
    const response1 = await fetch(`${baseURL}/api/v1/dashboard/summary?period_days=30`, { headers });
    const data1 = await response1.json();
    console.log('Response without filter:', {
      status: response1.status,
      totalCost: data1?.cost_summary?.totals?.total_cost || 0,
      topRegions: data1?.top_regions?.length || 0
    });
    
    // Test 2: Dashboard summary WITH Oracle Cloud filter
    console.log('\n🔶 Test 2: Dashboard summary WITH Oracle Cloud filter');
    const response2 = await fetch(`${baseURL}/api/v1/dashboard/summary?period_days=30&provider_name=Oracle%20Cloud`, { headers });
    const data2 = await response2.json();
    console.log('Response with Oracle Cloud filter:', {
      status: response2.status,
      totalCost: data2?.cost_summary?.totals?.total_cost || 0,
      topRegions: data2?.top_regions?.length || 0,
      providerUsed: 'Oracle Cloud'
    });
    
    // Test 3: Provider distribution without filter
    console.log('\n📈 Test 3: Provider distribution without filter');
    const response3 = await fetch(`${baseURL}/api/v1/analytics/by-provider?days=30&top_n=10`, { headers });
    const data3 = await response3.json();
    console.log('Provider distribution without filter:', {
      status: response3.status,
      providers: data3?.data?.provider_breakdown?.map(p => ({
        name: p.provider_name,
        cost: p.total_cost,
        percentage: p.percentage_of_total
      })) || []
    });
    
    // Test 4: Provider distribution WITH Oracle Cloud filter
    console.log('\n🔶 Test 4: Provider distribution WITH Oracle Cloud filter');
    const response4 = await fetch(`${baseURL}/api/v1/analytics/by-provider?days=30&top_n=10&provider_name=Oracle%20Cloud`, { headers });
    const data4 = await response4.json();
    console.log('Provider distribution with Oracle Cloud filter:', {
      status: response4.status,
      providers: data4?.data?.provider_breakdown?.map(p => ({
        name: p.provider_name,
        cost: p.total_cost,
        percentage: p.percentage_of_total
      })) || []
    });
    
    console.log('\n✅ API testing completed!');
    
  } catch (error) {
    console.error('❌ API test failed:', error);
  }
};

// Execute the test
testOracleCloudAPI();