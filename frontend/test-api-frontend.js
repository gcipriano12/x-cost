// Test script para verificar a API do frontend
// Execute no console do browser: node test-api-frontend.js

const testAPI = async () => {
  console.log('🧪 Testing Forecast API from Frontend perspective...');
  
  const token = localStorage.getItem('access_token');
  console.log('Token:', token ? 'Present' : 'Missing');
  
  try {
    const response = await fetch('/api/v1/analytics/forecast?months=7', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    console.log('Status:', response.status);
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ Success Response:', data);
      console.log('📊 Structure:');
      console.log('- success:', data.success);
      console.log('- data.forecast_data length:', data.data?.forecast_data?.length);
      console.log('- data.metadata:', data.data?.metadata);
      console.log('- data.budget_info:', data.data?.budget_info);
    } else {
      const errorData = await response.json();
      console.log('❌ Error Response:', errorData);
    }
  } catch (error) {
    console.log('💥 Exception:', error);
  }
};

testAPI();
