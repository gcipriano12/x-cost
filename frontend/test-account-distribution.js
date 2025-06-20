// Script para testar o novo endpoint de account distribution
// Execute no console do navegador em http://localhost:8080

console.log('🔧 Setting updated admin token for account distribution test...');

// Novo token válido
const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc1MDQwMTE3MCwiaWF0IjoxNzUwMzk3NTcwLCJ0eXBlIjoiYWNjZXNzX3Rva2VuIn0.HWlE5HTT7hWO0MO3lEV7bOv8LnCwLJCKiGFfHIv6s_g";

// Limpar e definir token
localStorage.clear();
localStorage.setItem('access_token', token);

console.log('✅ Token set successfully');
console.log('🧪 Testing account distribution endpoint...');

// Testar diretamente a API de account distribution
fetch('/api/v1/dashboard/account-distribution?provider=Oracle&time_filter=30d', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => {
  console.log('✅ Account distribution API test:', data);
  if (data.success && data.data.length > 0) {
    console.log(`📊 Found ${data.data.length} accounts for Oracle:`, data.data);
  }
})
.catch(error => {
  console.error('❌ Account distribution API test failed:', error);
});

console.log('🔄 Reloading page to test frontend integration...');
setTimeout(() => window.location.reload(), 2000);
