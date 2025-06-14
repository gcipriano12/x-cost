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

// Tipos para Dashboard Summary - Atualizado para corresponder à API real
export interface DashboardSummary {
  metrics: {
    total_cost: string; // API retorna como string
    cost_change_percentage: string; // API retorna como string
    monthly_average: string; // API retorna como string
    top_service: {
      service_name: string;
      provider_name: string;
      total_cost: number;
    };
    annual_projection: string; // API retorna como string
    budget_consumption: {
      total_budget: number;
      current_spend: number;
      consumption_percentage: number;
      remaining_budget: number;
    };
  };
  provider_distribution: {
    provider_name: string;
    total_cost: string; // API retorna como string
    percentage: string; // API retorna como string
    cost_change: number | null;
  }[];
  highlights: {
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
  };
  generated_at: string;
  period: {
    start_date: string;
    end_date: string;
    days: number;
  };
}
