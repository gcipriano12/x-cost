// Script para testar Virtual Tags no navegador
// Cole este código no console do navegador (F12 > Console)

console.log('🚀 Configurando token para Virtual Tags...');

// Token válido
const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0Iiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzUwNDkxMTQ2LCJpYXQiOjE3NTA0ODc1NDYsInR5cGUiOiJhY2Nlc3NfdG9rZW4ifQ.n4KqX0yh-Lu_USVPCDqJJUZFYno7_WDU01iAvGMvGKk";

// Definir o token no localStorage
localStorage.setItem('access_token', token);

// Verificar se foi definido corretamente
console.log('✅ Token definido:', localStorage.getItem('access_token'));

// Navegar para Virtual Tags
console.log('📍 Navegando para /virtual-tags...');
window.location.href = '/virtual-tags';
