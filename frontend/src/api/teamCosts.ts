import { TeamCostsResponse } from '../types/teamCosts';
import { apiClient } from './client';

export const teamCostsApi = {
  /**
   * Busca dados de custos por equipe
   * @param timePeriod - Período para análise (30d, 7d, 90d, this-year, previous-year, custom)
   * @param customStartDate - Data de início para período customizado (YYYY-MM-DD)
   * @param customEndDate - Data de fim para período customizado (YYYY-MM-DD)
   * @param provider - Provedor a filtrar (opcional)
   * @param accountId - ID da conta a filtrar (opcional)
   * @param environment - Ambiente a filtrar (opcional)
   * @param costCenter - Centro de custo a filtrar (opcional)
   * @param limit - Limite de resultados (opcional)
   * @returns Promise com dados de custos por equipe
   */
  getTeamCosts: async (params?: {
    timePeriod?: string;
    customStartDate?: string;
    customEndDate?: string;
    provider?: string;
    accountId?: string;
    environment?: string;
    costCenter?: string;
    limit?: number;
  }): Promise<TeamCostsResponse> => {
    const queryParams = new URLSearchParams();
    
    if (params?.timePeriod) {
      queryParams.append('time_period', params.timePeriod);
    }
    
    if (params?.customStartDate) {
      queryParams.append('custom_start_date', params.customStartDate);
    }
    
    if (params?.customEndDate) {
      queryParams.append('custom_end_date', params.customEndDate);
    }
    
    if (params?.provider) {
      queryParams.append('provider', params.provider);
    }
    
    if (params?.accountId) {
      queryParams.append('account_id', params.accountId);
    }
    
    if (params?.environment) {
      queryParams.append('environment', params.environment);
    }
    
    if (params?.costCenter) {
      queryParams.append('cost_center', params.costCenter);
    }
    
    if (params?.limit) {
      queryParams.append('limit', params.limit.toString());
    }
    
    const url = `/team-costs${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await apiClient.get<TeamCostsResponse>(url);
    
    return response.data;
  }
};
