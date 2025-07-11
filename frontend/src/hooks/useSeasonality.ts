import { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import { useToast } from './use-toast';

export interface SeasonalityData {
  monthlyComparison: number;      // 0-100
  weeklyPattern: number;          // 0-100  
  seasonalProgress: number;       // 0-100
  trendVariation: number;         // 0-100
  status: 'normal' | 'attention' | 'alert';
  lastUpdated: string;
  metadata?: {
    historicalMonths: number;
    dataQuality: string;
    nextPeakExpected: string;
  };
}

export const useSeasonality = () => {
  const [data, setData] = useState<SeasonalityData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  const fetchSeasonality = async (forceRefresh = false) => {
    setLoading(true);
    setError(null);
    try {
      console.log('🔄 Fetching seasonality data...');
      
      // Verificar se há token
      const token = localStorage.getItem('access_token');
      console.log('🔑 Token exists:', !!token);
      if (!token) {
        throw new Error('No access token found - user not logged in');
      }
      
      // Adicionar timestamp para evitar cache
      const url = forceRefresh 
        ? `/api/v1/analytics/seasonality?_t=${Date.now()}` 
        : '/api/v1/analytics/seasonality';
      
      console.log('🌐 Making request to:', url);
      console.log('🌐 Using token:', token.substring(0, 20) + '...');
      
      const response = await apiClient.get<SeasonalityData>(url);
      console.log('✅ Seasonality data received:', response.data);
      setData(response.data);
    } catch (error: any) {
      console.error('❌ Seasonality fetch error:', error);
      const errorMessage = error.response?.data?.detail || error.message || "Failed to load seasonality data";
      setError(errorMessage);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const retry = () => {
    fetchSeasonality(true);
  };

  useEffect(() => {
    fetchSeasonality(true);
    
    // Refresh automático a cada hora
    const interval = setInterval(() => {
      fetchSeasonality(false);
    }, 60 * 60 * 1000); // 1 hora
    
    return () => clearInterval(interval);
  }, []);

  return {
    data,
    loading,
    error,
    retry,
    refresh: () => fetchSeasonality(true),
  };
};