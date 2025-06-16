// Sistema de cores harmonizado para gráficos do X-Cost
// Usando paleta de cores consistente e acessível

/**
 * Cores para provedores de nuvem (seguindo padrão visual dos cards)
 * Baseado na paleta suave e elegante vista nos cards do dashboard
 * Cores mais suaves e transparentes para harmonizar com o design
 */
export const PROVIDER_COLORS = {
  AWS: '#FBB040',              // Laranja suave e elegante
  Azure: '#4A9EF1',           // Azul suave similar ao card de forecast
  GCP: '#7BA7F7',             // Azul claro suave diferenciado
  'Oracle Cloud': '#EF4444',  // Vermelho igual ao High Effort (bg-red-500)
  'Google Cloud': '#7BA7F7',  // Alias para GCP
  'Microsoft Azure': '#4A9EF1', // Nome completo do Azure
  'Amazon Web Services': '#FBB040', // Nome completo da AWS
} as const;

/**
 * Cores para categorias de serviços (seguindo padrão visual dos cards)
 * Paleta harmoniosa que combina com o design elegante do site
 * Cores mais suaves e transparentes para harmonizar com o design
 */
export const CATEGORY_COLORS = {
  'Computation': '#34D399',    // Verde suave similar ao card de savings
  'Storage': '#A78BFA',       // Roxo/Violeta suave e transparente
  'Network': '#67E8F9',       // Ciano suave e elegante
  'Database': '#FBB040',      // Âmbar suave/Dourado
  'Security': '#F87171',      // Vermelho suave similar ao waste
  'AI/ML': '#F472B6',         // Rosa/Magenta suave
  'Monitoring': '#34D399',    // Verde monitoramento suave
  'Analytics': '#4A9EF1',     // Azul analytics suave
  'Others': '#9CA3AF',        // Cinza neutro mais diferenciado do Storage
  'Serverless': '#6EE7B7',    // Verde mais suave
  'Container': '#FBB040',     // Laranja suave
  'Management': '#A78BFA',    // Violeta suave
} as const;

/**
 * Paleta de cores secundárias (seguindo padrão dos cards)
 * Cores mais suaves e transparentes para harmonizar com o design
 */
export const ACCENT_COLORS = {
  success: '#34D399',         // Verde suave similar ao card de savings
  warning: '#FBB040',         // Âmbar suave para avisos
  error: '#F87171',           // Vermelho suave similar ao card de waste
  info: '#4A9EF1',            // Azul suave similar ao card de forecast
  neutral: '#9CA3AF',         // Cinza neutro mais suave
} as const;

/**
 * Obtém cor do provedor
 */
export function getProviderColor(provider: string): string {
  const normalizedProvider = normalizeProviderName(provider);
  return PROVIDER_COLORS[normalizedProvider as keyof typeof PROVIDER_COLORS] || ACCENT_COLORS.neutral;
}

/**
 * Obtém cor da categoria
 */
export function getCategoryColor(category: string): string {
  return CATEGORY_COLORS[category as keyof typeof CATEGORY_COLORS] || CATEGORY_COLORS.Others;
}

/**
 * Normaliza nome do provedor
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
  
  return provider;
}

/**
 * Obtém array de cores para gráficos (mix de providers e categories)
 */
export function getChartColorPalette(): string[] {
  return [
    ...Object.values(PROVIDER_COLORS),
    ...Object.values(CATEGORY_COLORS),
    ...Object.values(ACCENT_COLORS)
  ];
}

/**
 * Obtém cor baseada no índice (para gráficos dinâmicos)
 */
export function getColorByIndex(index: number): string {
  const palette = getChartColorPalette();
  return palette[index % palette.length];
}