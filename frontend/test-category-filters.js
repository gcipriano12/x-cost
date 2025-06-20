// Script para testar os filtros de categoria no frontend
// Execute no console do navegador em http://localhost:8080

console.log('🔧 Testing category distribution with provider filters...');

// Definir token
const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc1MDM5NDM2MiwiaWF0IjoxNzUwMzkwNzYyLCJ0eXBlIjoiYWNjZXNzX3Rva2VuIn0.U_RBB_dD1p44MrBjDvmpzBZevpLuofPJ-c-J8oFyauU";
localStorage.setItem('access_token', token);

console.log('✅ Token set, reloading page...');

// Recarregar para aplicar token
window.location.reload();

// Adicionar listeners para testar filtros após reload
setTimeout(() => {
  console.log('🎯 Testing provider filters...');
  
  // Simular click nos filtros de provedor
  const providerButtons = document.querySelectorAll('[data-provider]');
  console.log(`Found ${providerButtons.length} provider buttons`);
  
  providerButtons.forEach((button, index) => {
    const provider = button.getAttribute('data-provider');
    console.log(`Button ${index}: ${provider}`);
  });
  
  // Verificar se há erros no console
  const originalError = console.error;
  let errorCount = 0;
  
  console.error = function(...args) {
    errorCount++;
    console.log(`❌ Error ${errorCount}:`, ...args);
    originalError.apply(console, args);
  };
  
  console.log('🔍 Error monitoring enabled');
}, 3000);
