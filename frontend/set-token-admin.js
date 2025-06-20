// Script para definir token de administrador no localStorage do frontend
// Para usar: execute este script no console do navegador em http://localhost:8080

console.log('🔧 Setting admin token...');

const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc1MDM5Nzc2OSwiaWF0IjoxNzUwMzk0MTY5LCJ0eXBlIjoiYWNjZXNzX3Rva2VuIn0.sA6JTBLBJLyMnVdZM4v5mGlq9J9VJJ35G-cLZs1g5lI";

// Definir token no localStorage
localStorage.setItem('access_token', token);

// Verificar se foi definido
const savedToken = localStorage.getItem('access_token');
console.log('✅ Token set:', savedToken ? 'YES' : 'NO');
console.log('🔑 Token length:', savedToken?.length);
console.log('🔑 Token preview:', savedToken?.substring(0, 50) + '...');

// Recarregar a página para aplicar o token
console.log('🔄 Reloading page to apply token...');
window.location.reload();
