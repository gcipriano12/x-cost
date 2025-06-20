Passo 1: Abrir o Console do Navegador

1. Abra o navegador na página do frontend
2. Pressione F12 (ou clique direito > Inspecionar)
3. Vá para a aba Console

Passo 2: Copiar e Colar o Script

Copie este código completo e cole no console:

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

Passo 3: Pressionar Enter
- Cole o código e pressione Enter
- O script será executado automaticamente

🎯 O que Acontece:
1. 🔄 Obtendo novo token... - Faz login no backend
2. ✅ Novo token obtido e definido! - Salva no localStorage
3. 🔑 Token: eyJhbGci... - Mostra início do token
4. ⏰ Expira em: 3600 segundos - Mostra tempo de expiração
5. 🔄 Recarregando página... - Recarrega automaticamente

📋 Resultado:
- Página recarrega com token válido
- Distribuição por Categoria mostra dados reais
- Console limpo sem erros 401
- Todos os filtros funcionando

É só copiar, colar e pressionar Enter! 🚀