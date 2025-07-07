const fs = require('fs');
const path = require('path');

// Mensagem de segurança
console.log('⚠️ Este script foi desativado por motivos de segurança');
console.log('Para configurar um token de acesso, siga estas etapas:');
console.log('1. Gere um novo token usando a ferramenta de autenticação apropriada');
console.log('2. Configure manualmente o token no localStorage do navegador');
console.log('3. Use as ferramentas de desenvolvimento para verificar a resposta da API');

// Versão segura do script
const browserScript = `
// Instruções para configurar token manualmente
console.log('⚠️ Por motivos de segurança, configure o token manualmente:');
console.log('1. Obtenha um token válido do sistema de autenticação');
console.log('2. Execute: localStorage.setItem("access_token", "seu-token-aqui")');
console.log('3. Recarregue a página para ativar o novo token');

// Exemplo de como testar a API (sem expor tokens)
const testParams = new URLSearchParams({
  months: '7',
  start_date: '2024-07-07',
  end_date: '2025-07-07'
});

console.log('📋 Para testar a API, execute:');
console.log(\`fetch('/api/v1/analytics/forecast?\${testParams.toString()}', {
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('access_token'),
    'Content-Type': 'application/json'
  }
})
.then(r => r.ok ? r.json() : r.text().then(t => Promise.reject(\`\${r.status}: \${t}\`)))
.then(d => console.log('✅ Success:', d))
.catch(e => console.log('❌ Error:', e));\`);
`;

// Salvar script seguro
fs.writeFileSync(path.join(__dirname, 'browser-script-secure.js'), browserScript);
console.log('\n💾 Script seguro salvo em browser-script-secure.js');
