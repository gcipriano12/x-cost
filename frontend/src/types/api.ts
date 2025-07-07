// Tipos de autenticação
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
}

// Tipos de credenciais AWS
export interface AWSCredentials {
  id?: number;
  name: string;
  aws_access_key_id: string;
  aws_secret_access_key: string;
  aws_region: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface CredentialsResponse {
  id: number;
  name: string;
  aws_region: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Tipos de analytics
export interface CostData {
  date: string;
  amount: number;
  currency: string;
  service?: string;
  region?: string;
}

export interface TrendData {
  period: string;
  total_cost: number;
  change_percentage: number;
  previous_period_cost: number;
}

export interface ServiceCost {
  service_name: string;
  cost: number;
  percentage: number;
  change_from_previous: number;
}

export interface RegionCost {
  region: string;
  cost: number;
  percentage: number;
  services_count: number;
}

export interface MonthlyBreakdown {
  month: string;
  total_cost: number;
  services: ServiceCost[];
  regions: RegionCost[];
}

export interface APIError {
  detail: string;
  status_code: number;
}

// Tipos para Account Distribution
export interface AccountDistribution {
  account_id: string;
  billing_account_name: string;
  provider_name: string;
  total_cost: string; // API retorna como string
  percentage: string; // API retorna como string
  cost_change?: number | null;
}

// Tipos para Dashboard Summary - Atualizado para corresponder à API real
// Tipos para Forecast Data
export interface ForecastDataPoint {
  month: string;
  actual?: number;
  forecast?: number;
  budget?: number;
  variance?: number;
  confidence_interval?: {
    lower: number;
    upper: number;
  };
}

export interface ForecastResponse {
  period: {
    start_date: string;
    end_date: string;
    forecast_months: number;
  };
  generated_at: string;
  forecast_data: ForecastDataPoint[];
  metadata: {
    model_accuracy: number;
    confidence_level: number;
    data_completeness: number;
    forecast_method: string;
  };
  budget_info?: {
    total_budget: number;
    monthly_budget: number;
    budget_exceeded_months: string[];
  };
}

export interface DashboardSummary {
  period: {
    start_date: string;
    end_date: string;
    label: string;
  };
  generated_at: string;
  cost_summary: {
    period: {
      start_date: string;
      end_date: string;
      label: string;
    };
    totals: {
      total_cost: number;
      average_cost: number;
      record_count: number;
    };
    provider: string;
    generated_at: string;
  };
  top_services: {
    service_name: string;
    category: string;
    total_cost: number;
    avg_cost: number;
    record_count: number;
    percentage_of_total: number;
  }[];
  top_regions: {
    region: string;
    total_cost: number;
    avg_cost: number;
    record_count: number;
    percentage_of_total: number;
  }[];
  budget_summary: {
    total_budgets: number;
    active_budgets: number;
    total_budget_amount: number;
    budgets: {
      id: number;
      name: string;
      amount: number;
      is_active: boolean;
    }[];
  };
  cost_trend: {
    period: string;
    total_cost: number;
    record_count: number;
    trend_percentage: number | null;
    cost_change: number;
    trend_direction: string;
    growth_rate: number;
  }[];
  // Campos opcionais para compatibilidade com componentes existentes
  provider_distribution?: {
    provider_name: string;
    total_cost: string;
    percentage: string;
    cost_change: number | null;
  }[];
  account_distribution?: AccountDistribution[];
  highlights?: {
    next_month_forecast: {
      amount: number;
      change_percentage: number;
    };
    estimated_waste: {
      amount: number;
      percentage: number;
      total_cost: number;
    };
    savings_achieved: {
      amount: number;
      percentage: number;
    };
    annual_projection?: {
      amount: number;
      growth_rate_annual: number;
      base_annual_cost: number;
      period_coverage: number;
    };
    monthly_average?: {
      amount: number;
      period_months: number;
      period_description: string;
      total_cost: number;
    };
  };
  metrics?: {
    total_cost: string;
    cost_change_percentage: string;
    monthly_average: string;
    top_service: {
      service_name: string;
      provider_name: string;
      total_cost: number;
    };
    annual_projection: string;
    budget_consumption: {
      total_budget: number;
      current_spend: number;
      consumption_percentage: number;
      remaining_budget: number;
    };
  };
}
