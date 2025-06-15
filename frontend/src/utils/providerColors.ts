// Re-exportar funcionalidades do sistema centralizado de cores
import { PROVIDER_COLORS as CHART_PROVIDER_COLORS } from './chartColors';

export { 
  getProviderColor, 
  normalizeProviderName
} from './chartColors';

export const PROVIDER_COLORS = CHART_PROVIDER_COLORS;
export type CloudProvider = keyof typeof PROVIDER_COLORS;

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
