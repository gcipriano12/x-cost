// Cores padronizadas para provedores de nuvem
export const PROVIDER_COLORS = {
  AWS: '#FF9900',        // Laranja oficial da AWS
  Azure: '#0078D4',      // Azul oficial da Microsoft Azure
  GCP: '#4285F4',        // Azul oficial do Google Cloud Platform
  'Oracle Cloud': '#F80000',  // Vermelho oficial da Oracle
  'Google Cloud': '#4285F4',  // Alias para GCP
  'Microsoft Azure': '#0078D4', // Nome completo do Azure
  'Amazon Web Services': '#FF9900', // Nome completo da AWS
} as const;

export type CloudProvider = keyof typeof PROVIDER_COLORS;

/**
 * Obtém a cor padronizada para um provedor de nuvem
 * @param provider Nome do provedor
 * @returns Cor em formato hexadecimal
 */
export function getProviderColor(provider: string): string {
  // Normalizar o nome do provedor
  const normalizedProvider = normalizeProviderName(provider);
  
  return PROVIDER_COLORS[normalizedProvider as CloudProvider] || '#6B7280'; // Cor padrão cinza
}

/**
 * Normaliza o nome do provedor para garantir consistência
 * @param provider Nome do provedor
 * @returns Nome normalizado do provedor
 */
export function normalizeProviderName(provider: string): string {
  const providerLower = provider.toLowerCase().trim();
  
  if (providerLower.includes('aws') || providerLower.includes('amazon')) {
    return 'AWS';
  }
  
  if (providerLower.includes('azure') || providerLower.includes('microsoft')) {
    return 'Azure';
  }
  
  if (providerLower.includes('gcp') || providerLower.includes('google')) {
    return 'GCP';
  }
  
  if (providerLower.includes('oracle')) {
    return 'Oracle Cloud';
  }
  
  // Se não reconhecer, retorna o nome original
  return provider;
}

/**
 * Identifica o provedor baseado no nome da região
 * @param region Nome da região
 * @returns Nome normalizado do provedor
 */
export function getProviderFromRegion(region: string): string {
  const regionLower = region.toLowerCase();
  
  if (regionLower.includes('us-') || regionLower.includes('sa-') || regionLower.includes('eu-') || regionLower.includes('ap-')) {
    return 'AWS';
  }
  
  if (regionLower.includes('east') || regionLower.includes('brazil') || regionLower.includes('west') || regionLower.includes('central') && regionLower.includes('us')) {
    return 'Azure';
  }
  
  if (regionLower.includes('central') && !regionLower.includes('us')) {
    return 'GCP';
  }
  
  return 'Oracle Cloud';
}

/**
 * Obtém todas as cores dos provedores como array para gráficos
 */
export function getAllProviderColors(): string[] {
  return Object.values(PROVIDER_COLORS);
}
