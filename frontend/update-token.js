// Script para definir o novo token no localStorage
const newToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0Iiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzUwNTI1MjM1LCJpYXQiOjE3NTA1MTgwMzUsInR5cGUiOiJhY2Nlc3NfdG9rZW4ifQ.tUqLbVRFDAhpGZhh-HptRAd8yqwV1XQSsn6g6V2V13M';

localStorage.setItem('access_token', newToken);
console.log('✅ Token atualizado no localStorage');
console.log('🔄 Recarregando a página...');
window.location.reload();
