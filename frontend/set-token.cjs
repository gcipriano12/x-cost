const fs = require('fs');
const path = require('path');

// Ler token do arquivo
const tokenPath = path.join(__dirname, 'current-token.txt');
const token = fs.readFileSync(tokenPath, 'utf8').trim();

console.log('🔑 Setting token in localStorage...');
console.log(`Token: ${token.substring(0, 50)}...`);

// Script que deve ser executado no console do browser
const browserScript = `
// Definir token no localStorage
localStorage.setItem('access_token', '${token}');
console.log('✅ Token set in localStorage');
console.log('Token:', localStorage.getItem('access_token')?.substring(0, 50) + '...');

// Testar a API
fetch('/api/v1/analytics/forecast?months=7', {
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('access_token'),
    'Content-Type': 'application/json'
  }
})
.then(response => {
  console.log('API Response Status:', response.status);
  if (response.ok) {
    return response.json();
  } else {
    return response.text().then(text => Promise.reject(\`\${response.status}: \${text}\`));
  }
})
.then(data => {
  console.log('✅ API Success:', data);
  console.log('Forecast points:', data.data?.forecast_data?.length);
})
.catch(error => {
  console.log('❌ API Error:', error);
});
`;

console.log('\n📋 Execute this in browser console:');
console.log('=====================================');
console.log(browserScript);
console.log('=====================================');

// Também salvar o script em um arquivo
fs.writeFileSync(path.join(__dirname, 'browser-script.js'), browserScript);
console.log('\n💾 Script saved to browser-script.js');
