// Script para definir o token de acesso no localStorage
// Execute este script no console do navegador (F12 > Console)

localStorage.setItem('access_token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc1MDQ1NjY3OCwiaWF0IjoxNzUwMzcwMjc4LCJ0eXBlIjoiYWNjZXNzX3Rva2VuIn0.N4xeJOZL5lAnDDIqK-bI3AcH1o5su0qq5SC0ql1ssZw');

console.log('✅ Token configurado com sucesso!');
console.log('📄 Agora recarregue a página para ver os dados do MegaBill');

// Recarregar a página automaticamente após definir o token
setTimeout(() => {
    location.reload();
}, 1000);
