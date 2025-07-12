// Enums para categorias
export enum KPICategory {
  EFFICIENCY = 'efficiency',
  PRICING = 'pricing',
  PLANNING = 'planning',
  GOVERNANCE = 'governance'
}

// Status do KPI
export type KPIStatus = 'good' | 'warning' | 'critical' | 'neutral';

// Interface principal do KPI
export interface KPIValue {
  kpi_id: string;
  code: string;
  name: string;
  category: KPICategory;
  value: number;
  unit?: string;
  target?: number;
  trend?: number;
  is_good_when_higher: boolean;
  status: KPIStatus;
  last_updated: string;
  metadata?: Record<string, any>;
}

// Resposta agrupada por categoria
export interface KPICategoryResponse {
  category: KPICategory;
  kpis: KPIValue[];
  summary: {
    total_kpis: number;
    status_distribution: {
      good: number;
      warning: number;
      critical: number;
    };
    health_score: number;
    average_trend: number;
  };
}

// Configuração de KPI
export interface KPIConfig {
  kpi_id: string;
  target_value?: number;
  warning_threshold?: number;
  critical_threshold?: number;
  is_enabled: boolean;
}

// Mapeamento de cores por categoria
export const KPI_CATEGORY_COLORS: Record<KPICategory, string> = {
  [KPICategory.EFFICIENCY]: '#3b82f6', // blue
  [KPICategory.PRICING]: '#8b5cf6',    // purple
  [KPICategory.PLANNING]: '#f97316',   // orange
  [KPICategory.GOVERNANCE]: '#10b981'  // green
};

// Mapeamento de ícones por status
export const KPI_STATUS_ICONS = {
  good: 'CheckCircle',
  warning: 'AlertTriangle',
  critical: 'XCircle',
  neutral: 'Circle'
};