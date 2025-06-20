// Script para definir o token no localStorage do navegador
// Execute este script no console do navegador (F12 > Console)

const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc1MDM5Mjc0OSwiaWF0IjoxNzUwMzg5MTQ5LCJ0eXBlIjoiYWNjZXNzX3Rva2VuIn0.Qi7ae0yaxmjSzehMcYHjxcM-Ve_roz8QmoLIhRiUxZs";

// Definir o token no localStorage
localStorage.setItem('access_token', token);

// Verificar se foi definido corretamente
console.log('✅ Token definido:', localStorage.getItem('access_token'));

// Recarregar a página para aplicar o token
window.location.reload();