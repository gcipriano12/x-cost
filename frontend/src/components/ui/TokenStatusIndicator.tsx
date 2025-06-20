import React, { useState, useEffect } from 'react';
import { Badge } from '@/components/ui/badge';
import { Clock, AlertTriangle, CheckCircle } from 'lucide-react';
import { tokenManager, TokenInfo, formatTimeUntilExpiry, isTokenNearExpiry } from '@/utils/tokenManager';

export const TokenStatusIndicator: React.FC = () => {
  const [tokenInfo, setTokenInfo] = useState<TokenInfo | null>(null);

  useEffect(() => {
    // Atualizar informações do token a cada 30 segundos
    const updateTokenInfo = () => {
      setTokenInfo(tokenManager.getTokenInfo());
    };

    updateTokenInfo();
    const interval = setInterval(updateTokenInfo, 30000);

    return () => clearInterval(interval);
  }, []);

  if (!tokenInfo) {
    return (
      <Badge variant="destructive" className="flex items-center gap-1">
        <AlertTriangle className="h-3 w-3" />
        Token não encontrado
      </Badge>
    );
  }

  if (!tokenInfo.isValid) {
    return (
      <Badge variant="destructive" className="flex items-center gap-1">
        <AlertTriangle className="h-3 w-3" />
        Token expirado
      </Badge>
    );
  }

  const isNearExpiry = isTokenNearExpiry(tokenInfo);
  const timeLeft = formatTimeUntilExpiry(tokenInfo.timeUntilExpiry);

  return (
    <Badge 
      variant={isNearExpiry ? "destructive" : "secondary"} 
      className="flex items-center gap-1"
    >
      {isNearExpiry ? (
        <AlertTriangle className="h-3 w-3" />
      ) : (
        <CheckCircle className="h-3 w-3" />
      )}
      <Clock className="h-3 w-3" />
      {timeLeft}
    </Badge>
  );
};
