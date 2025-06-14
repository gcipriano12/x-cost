
import { useState } from 'react';
import { apiClient } from '../api/client';
import { TrendData, ServiceCost, RegionCost, MonthlyBreakdown } from '../types/api';
import { useToast } from './use-toast';

interface DateRange {
  startDate?: Date;
  endDate?: Date;
}

export const useAnalytics = () => {
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const getTrend = async (
    credentialId: number, 
    days: number = 30, 
    dateRange?: DateRange
  ): Promise<TrendData[]> => {
    setLoading(true);
    try {
      let url = `/api/v1/analytics/trend?credential_id=${credentialId}`;
      
      if (dateRange?.startDate && dateRange?.endDate) {
        const startDate = dateRange.startDate.toISOString().split('T')[0];
        const endDate = dateRange.endDate.toISOString().split('T')[0];
        url += `&start_date=${startDate}&end_date=${endDate}`;
      } else {
        url += `&days=${days}`;
      }
      
      const response = await apiClient.get<TrendData[]>(url);
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

  const getServiceCosts = async (
    credentialId: number, 
    days: number = 30, 
    dateRange?: DateRange
  ): Promise<ServiceCost[]> => {
    setLoading(true);
    try {
      let url = `/api/v1/analytics/by-service?credential_id=${credentialId}`;
      
      if (dateRange?.startDate && dateRange?.endDate) {
        const startDate = dateRange.startDate.toISOString().split('T')[0];
        const endDate = dateRange.endDate.toISOString().split('T')[0];
        url += `&start_date=${startDate}&end_date=${endDate}`;
      } else {
        url += `&days=${days}`;
      }
      
      const response = await apiClient.get<ServiceCost[]>(url);
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

  const getRegionCosts = async (
    credentialId: number, 
    days: number = 30, 
    dateRange?: DateRange
  ): Promise<RegionCost[]> => {
    setLoading(true);
    try {
      let url = `/api/v1/analytics/by-region?credential_id=${credentialId}`;
      
      if (dateRange?.startDate && dateRange?.endDate) {
        const startDate = dateRange.startDate.toISOString().split('T')[0];
        const endDate = dateRange.endDate.toISOString().split('T')[0];
        url += `&start_date=${startDate}&end_date=${endDate}`;
      } else {
        url += `&days=${days}`;
      }
      
      const response = await apiClient.get<RegionCost[]>(url);
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
