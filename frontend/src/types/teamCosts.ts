/**
 * Team costs related types and interfaces
 */

export interface TeamCostItem {
  team_name: string;
  total_cost: number;
  percentage: number;
  resource_count: number;
  avg_cost_per_resource: number;
  color: string;
}

export interface TeamCostsResponse {
  success: boolean;
  data: TeamCostItem[];
  total_cost: number;
  period: string;
  team_count: number;
  last_updated: string;
  metadata: {
    query_params?: {
      time_period?: string;
      provider?: string;
      account_id?: string;
      environment?: string;
      cost_center?: string;
    };
    data_source?: string;
    aggregation_method?: string;
    message?: string;
  };
}

export interface TeamCostsRequest {
  time_period?: string;
  provider?: string;
  account_id?: string;
  environment?: string;
  cost_center?: string;
  limit?: number;
}

export interface TeamDetails {
  team_name: string;
  period: string;
  services: Array<{
    provider: string;
    service_name: string;
    cost: number;
    resource_count: number;
  }>;
  total_services: number;
}

// Chart data formats for visualization
export interface TeamCostChartData {
  name: string;
  value: number;
  percentage: number;
  color: string;
  fullName?: string;
}

export interface TeamCostsSummary {
  totalTeams: number;
  totalCost: number;
  highestTeam: {
    name: string;
    cost: number;
    percentage: number;
  };
  lowestTeam: {
    name: string;
    cost: number;
    percentage: number;
  };
}
