// Utilitário para gerenciamento de tokens JWT
import { toast } from '@/hooks/use-toast';

export interface TokenInfo {
  token: string;
  expiresAt: number;
  isValid: boolean;
  timeUntilExpiry: number;
}

/**
 * Decodifica um JWT token e extrai informações de expiração
 */
export function decodeToken(token: string): TokenInfo | null {
  try {
    // Extrair o payload do JWT (parte do meio)
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null;
    }

    // Decodificar o payload (base64url decode)
    const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')));
    
    const now = Math.floor(Date.now() / 1000);
    const expiresAt = payload.exp;
    const timeUntilExpiry = expiresAt - now;
    
    return {
      token,
      expiresAt,
      isValid: timeUntilExpiry > 0,
      timeUntilExpiry
    };
  } catch (error) {
    console.error('Erro ao decodificar token:', error);
    return null;
  }
}

/**
 * Verifica se o token está próximo da expiração (menos de 5 minutos)
 */
export function isTokenNearExpiry(tokenInfo: TokenInfo): boolean {
  return tokenInfo.timeUntilExpiry < 300; // 5 minutos
}

/**
 * Formata o tempo restante em formato legível
 */
export function formatTimeUntilExpiry(seconds: number): string {
  if (seconds <= 0) return 'Expirado';
  
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  return `${minutes}m`;
}

/**
 * Gerenciador de token com notificações automáticas
 */
export class TokenManager {
  private checkInterval: NodeJS.Timeout | null = null;
  private lastWarningTime: number = 0;

  /**
   * Inicia o monitoramento do token
   */
  startMonitoring() {
    // Verificar a cada minuto
    this.checkInterval = setInterval(() => {
      this.checkTokenStatus();
    }, 60000);
    
    // Verificação inicial
    this.checkTokenStatus();
  }

  /**
   * Para o monitoramento do token
   */
  stopMonitoring() {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
    }
  }

  /**
   * Verifica o status do token atual
   */
  private checkTokenStatus() {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    const tokenInfo = decodeToken(token);
    if (!tokenInfo) return;

    // Se o token expirou, remover do localStorage
    if (!tokenInfo.isValid) {
      localStorage.removeItem('access_token');
      toast({
        title: "Sessão Expirada",
        description: "Sua sessão expirou. Por favor, faça login novamente.",
        variant: "destructive",
      });
      return;
    }

    // Se está próximo da expiração e não avisamos recentemente
    if (isTokenNearExpiry(tokenInfo)) {
      const now = Date.now();
      // Só mostrar aviso a cada 2 minutos para não spammar
      if (now - this.lastWarningTime > 120000) {
        this.lastWarningTime = now;
        const timeLeft = formatTimeUntilExpiry(tokenInfo.timeUntilExpiry);
        
        toast({
          title: "Sessão Expirando",
          description: `Sua sessão expira em ${timeLeft}. Salve seu trabalho.`,
          variant: "destructive",
        });
      }
    }
  }

  /**
   * Obtém informações do token atual
   */
  getTokenInfo(): TokenInfo | null {
    const token = localStorage.getItem('access_token');
    if (!token) return null;
    
    return decodeToken(token);
  }
}

// Instância global do gerenciador de token
export const tokenManager = new TokenManager();
