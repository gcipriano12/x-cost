import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { TeamCostsResponse } from '../types/teamCosts';
import { teamCostsApi } from '../api/teamCosts';

interface UseTeamCostsParams {
  timePeriod?: string;
  customStartDate?: string;
  customEndDate?: string;
  provider?: string;
  accountId?: string;
  environment?: string;
  costCenter?: string;
  limit?: number;
  enabled?: boolean;
}

export const useTeamCosts = (params?: UseTeamCostsParams): UseQueryResult<TeamCostsResponse, Error> => {
  // Debug logging
  console.log('🎯 useTeamCosts called with params:', params);
  
  return useQuery<TeamCostsResponse, Error>({
    queryKey: ['team-costs', params],
    queryFn: () => {
      console.log('🔄 Making API call to team-costs with params:', params);
      return teamCostsApi.getTeamCosts(params);
    },
    enabled: params?.enabled !== false,
    staleTime: 1 * 60 * 1000, // Reduzido para 1 minuto para debug
    gcTime: 2 * 60 * 1000, // Reduzido para 2 minutos para debug
    retry: 2,
    refetchOnWindowFocus: false,
  });
};
