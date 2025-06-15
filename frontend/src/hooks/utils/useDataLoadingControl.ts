import { useRef } from 'react';

interface UseDataLoadingControlOptions {
  onParamsChange?: (params: string) => void;
}

export const useDataLoadingControl = (options: UseDataLoadingControlOptions = {}) => {
  const lastParamsRef = useRef<string>('');
  const isLoadingRef = useRef(false);

  const shouldSkipLoad = (params: string): boolean => {
    if (isLoadingRef.current) {
      return true;
    }

    // Para debug, permitir recarregamento mesmo com parâmetros iguais
    return false;
  };

  const startLoading = (params: string) => {
    isLoadingRef.current = true;
    lastParamsRef.current = params;
    options.onParamsChange?.(params);
  };

  const finishLoading = () => {
    isLoadingRef.current = false;
  };

  const createParamsKey = (
    credentialId: number,
    timeFilter?: string | number,
    provider?: string,
    dateRange?: string
  ): string => {
    const timestamp = Date.now();
    return `${credentialId}-${timeFilter || '30'}-${dateRange || 'none'}-${provider || 'all'}-${timestamp}`;
  };

  return {
    shouldSkipLoad,
    startLoading,
    finishLoading,
    createParamsKey,
    isLoading: () => isLoadingRef.current
  };
};
