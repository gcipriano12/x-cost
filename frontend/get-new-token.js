// Script para obter automaticamente um novo token e definir no localStorage
// Execute este script no console do navegador (F12 > Console)

async function getNewToken() {
  try {
    console.log('🔄 Obtendo novo token...');
    
    const response = await fetch('http://localhost:8000/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: 'admin',
        password: 'ChangeMe123!'
      })
    });
    
    if (!response.ok) {
      throw new Error(`Login failed: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (data.access_token) {
      // Definir o token no localStorage
      localStorage.setItem('access_token', data.access_token);
      
      console.log('✅ Novo token obtido e definido!');
      console.log('🔑 Token:', data.access_token.substring(0, 50) + '...');
      console.log('⏰ Expira em:', data.expires_in, 'segundos');
      
      // Recarregar a página para aplicar o token
      console.log('🔄 Recarregando página...');
      window.location.reload();
    } else {
      throw new Error('No access token in response');
    }
    
  } catch (error) {
    console.error('❌ Erro ao obter token:', error);
    console.log('🔧 Verifique se o backend está rodando em http://localhost:8000');
  }
}

// Executar automaticamente
getNewToken();