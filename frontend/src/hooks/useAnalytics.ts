
import { useState } from 'react';
import { apiClient } from '../api/client';
import { TrendData, ServiceCost, RegionCost, MonthlyBreakdown } from '../types/api';
import { useToast } from './use-toast';

export const useAnalytics = () => {
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const getTrend = async (credentialId: number, days: number = 30): Promise<TrendData[]> => {
    setLoading(true);
    try {
      const response = await apiClient.get<TrendData[]>(
        `/api/v1/analytics/trend?credential_id=${credentialId}&days=${days}`
      );
      return response.data;
    } catch (error: any) {
      toast({
        title: "Error loading trend data",
        description: error.response?.data?.detail || "Failed to load cost trends",
        variant: "destructive",
      });
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const getServiceCosts = async (credentialId: number, days: number = 30): Promise<ServiceCost[]> => {
    setLoading(true);
    try {
      const response = await apiClient.get<ServiceCost[]>(
        `/api/v1/analytics/by-service?credential_id=${credentialId}&days=${days}`
      );
      return response.data;
    } catch (error: any) {
      toast({
        title: "Error loading service costs",
        description: error.response?.data?.detail || "Failed to load service breakdown",
        variant: "destructive",
      });
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const getRegionCosts = async (credentialId: number, days: number = 30): Promise<RegionCost[]> => {
    setLoading(true);
    try {
      const response = await apiClient.get<RegionCost[]>(
        `/api/v1/analytics/by-region?credential_id=${credentialId}&days=${days}`
      );
      return response.data;
    } catch (error: any) {
      toast({
        title: "Error loading region costs",
        description: error.response?.data?.detail || "Failed to load region breakdown",
        variant: "destructive",
      });
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const getMonthlyReport = async (credentialId: number, month: string): Promise<MonthlyBreakdown> => {
    setLoading(true);
    try {
      const response = await apiClient.get<MonthlyBreakdown>(
        `/api/v1/analytics/monthly?credential_id=${credentialId}&month=${month}`
      );
      return response.data;
    } catch (error: any) {
      toast({
        title: "Error loading monthly report",
        description: error.response?.data?.detail || "Failed to load monthly data",
        variant: "destructive",
      });
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    getTrend,
    getServiceCosts,
    getRegionCosts,
    getMonthlyReport,
  };
};
