// Script para testar filtros de categoria - versão final
// Execute no console do navegador em http://localhost:8080

console.log('🔧 Setting final admin token...');

// Token atual válido
const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc1MDM5Nzc2OSwiaWF0IjoxNzUwMzk0MTY5LCJ0eXBlIjoiYWNjZXNzX3Rva2VuIn0.sA6JTBLBJLyMnVdZM4v5mGlq9J9VJJ35G-cLZs1g5lI";

// Limpar localStorage e definir novo token
localStorage.clear();
localStorage.setItem('access_token', token);

console.log('✅ Token set successfully');
console.log('🔄 Reloading page to test category filters...');

// Recarregar página
window.location.reload();
