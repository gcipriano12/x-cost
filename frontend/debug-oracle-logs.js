/**
 * Script para capturar logs do console relacionados ao Oracle Cloud
 * Para usar:
 * 1. Abra o console do navegador (F12)
 * 2. Cole este script e pressione Enter
 * 3. Selecione Oracle Cloud no dashboard
 * 4. Os logs serão capturados automaticamente
 */

// Interceptar console.log para capturar logs relevantes
const originalLog = console.log;
const originalWarn = console.warn;
const originalError = console.error;

let capturedLogs = [];

function captureLog(level, args) {
  const message = args.map(arg => 
    typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
  ).join(' ');
  
  // Filtrar logs relevantes para Oracle Cloud
  if (
    message.includes('Oracle Cloud') ||
    message.includes('Processing regions for provider filter') ||
    message.includes('Region:') ||
    message.includes('Fetching account distribution for provider') ||
    message.includes('oracle') &&
    (message.includes('API') || message.includes('request') || message.includes('response'))
  ) {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] ${level.toUpperCase()}: ${message}`;
    capturedLogs.push(logEntry);
    
    // Também mostrar no console original
    originalLog(`🔍 CAPTURED: ${logEntry}`);
  }
  
  // Chamar o console original
  switch(level) {
    case 'log': originalLog.apply(console, args); break;
    case 'warn': originalWarn.apply(console, args); break;
    case 'error': originalError.apply(console, args); break;
  }
}

// Sobrescrever métodos do console
console.log = (...args) => captureLog('log', args);
console.warn = (...args) => captureLog('warn', args);
console.error = (...args) => captureLog('error', args);

// Interceptar requisições fetch/axios
const originalFetch = window.fetch;
window.fetch = async (...args) => {
  const url = args[0];
  const options = args[1] || {};
  
  if (typeof url === 'string' && (
    url.includes('/api/v1/dashboard/summary') ||
    url.includes('/api/v1/dashboard/account-distribution')
  )) {
    console.log('🌐 FETCH REQUEST:', url, options);
    
    try {
      const response = await originalFetch.apply(window, args);
      const clonedResponse = response.clone();
      const data = await clonedResponse.json();
      
      console.log('🌐 FETCH RESPONSE:', url, {
        status: response.status,
        statusText: response.statusText,
        data: data
      });
      
      return response;
    } catch (error) {
      console.error('🌐 FETCH ERROR:', url, error);
      throw error;
    }
  }
  
  return originalFetch.apply(window, args);
};

// Interceptar XMLHttpRequest (usado pelo Axios)
const originalOpen = XMLHttpRequest.prototype.open;
const originalSend = XMLHttpRequest.prototype.send;

XMLHttpRequest.prototype.open = function(method, url, ...args) {
  this._interceptedUrl = url;
  this._interceptedMethod = method;
  return originalOpen.apply(this, [method, url, ...args]);
};

XMLHttpRequest.prototype.send = function(body) {
  const url = this._interceptedUrl;
  const method = this._interceptedMethod;
  
  if (url && (
    url.includes('/api/v1/dashboard/summary') ||
    url.includes('/api/v1/dashboard/account-distribution')
  )) {
    console.log('🌐 XHR REQUEST:', method, url, body);
    
    this.addEventListener('load', function() {
      try {
        const responseData = JSON.parse(this.responseText);
        console.log('🌐 XHR RESPONSE:', method, url, {
          status: this.status,
          statusText: this.statusText,
          data: responseData
        });
      } catch (e) {
        console.log('🌐 XHR RESPONSE (non-JSON):', method, url, {
          status: this.status,
          statusText: this.statusText,
          response: this.responseText
        });
      }
    });
    
    this.addEventListener('error', function() {
      console.error('🌐 XHR ERROR:', method, url, this.status, this.statusText);
    });
  }
  
  return originalSend.apply(this, [body]);
};

// Função para exportar logs capturados
window.exportOracleLogs = function() {
  const logsText = capturedLogs.join('\n');
  const blob = new Blob([logsText], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'oracle-cloud-logs.txt';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  
  console.log('📁 Logs exportados para oracle-cloud-logs.txt');
  return capturedLogs;
};

// Função para limpar logs
window.clearOracleLogs = function() {
  capturedLogs = [];
  console.log('🧹 Logs limpos');
};

// Função para mostrar logs capturados
window.showOracleLogs = function() {
  console.group('🔍 ORACLE CLOUD LOGS CAPTURADOS:');
  capturedLogs.forEach(log => console.log(log));
  console.groupEnd();
  return capturedLogs;
};

console.log('🚀 Script de captura Oracle Cloud ativado!');
console.log('📋 Comandos disponíveis:');
console.log('  - showOracleLogs(): Mostrar logs capturados');
console.log('  - exportOracleLogs(): Exportar logs para arquivo');
console.log('  - clearOracleLogs(): Limpar logs capturados');
console.log('🎯 Agora selecione Oracle Cloud no dashboard para capturar os logs...');