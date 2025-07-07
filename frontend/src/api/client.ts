import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token automaticamente
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  // Debug: Log das requisições para dashboard, analytics, forecast e services
  if (config.url?.includes('/dashboard/summary') || 
      config.url?.includes('/analytics/by-provider') ||
      config.url?.includes('/analytics/forecast') ||
      config.url?.includes('/services/top')) {
    console.log('🌐 API Request:', {
      url: config.url,
      method: config.method?.toUpperCase(),
      params: config.params,
      headers: config.headers,
      fullUrl: `${config.baseURL}${config.url}?${new URLSearchParams(config.params).toString()}`
    });
  }
  
  return config;
});

// Interceptor para tratar respostas e erros
apiClient.interceptors.response.use(
  (response) => {
    // Log de respostas de forecast para debug
    if (response.config.url?.includes('/analytics/forecast')) {
      console.log('✅ API Response Success:', {
        url: response.config.url,
        status: response.status,
        data: response.data
      });
    }
    return response;
  },
  (error) => {
    // Log de erros de forecast e services para debug
    if (error.config?.url?.includes('/analytics/forecast') || 
        error.config?.url?.includes('/services/top')) {
      console.log('❌ API Response Error:', {
        url: error.config.url,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        message: error.message
      });
    }

    if (error.response?.status === 401) {
      // Verificar se não estamos já na página de login para evitar loops
      const currentPath = window.location.pathname;
      if (currentPath !== '/login' && currentPath !== '/signup' && currentPath !== '/') {
        localStorage.removeItem('access_token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Serviços de API
export const dashboardService = {
  getSummary: (periodDays?: number, credentialId?: string, providerName?: string) => 
    apiClient.get('/api/v1/dashboard/summary', { 
      params: { 
        period_days: periodDays || 30, 
        credential_id: credentialId,
        provider_name: providerName
      } 
    })
};

export const analyticsService = {
  getCategoryDistribution: (params: {
    credentialId?: string;
    days?: number;
    startDate?: string;
    endDate?: string;
    topN?: number;
    providerName?: string;
  }) => 
    apiClient.get('/api/v1/analytics/by-category', { 
      params: {
        credential_id: params.credentialId,
        days: params.days,
        start_date: params.startDate,
        end_date: params.endDate,
        top_n: params.topN,
        provider_name: params.providerName
      }
    }),

  getProviderDistribution: (params: {
    credentialId?: string;
    days?: number;
    topN?: number;
    providerName?: string;
  }) => 
    apiClient.get('/api/v1/analytics/by-provider', { 
      params: {
        credential_id: params.credentialId,
        days: params.days,
        top_n: params.topN,
        provider_name: params.providerName
      }
    }),

  getForecastData: (params: {
    credentialId?: string;
    months?: number;
    startDate?: string;
    endDate?: string;
    providerName?: string;
  }) => 
    apiClient.get('/api/v1/analytics/forecast', { 
      params: {
        credential_id: params.credentialId,
        months: params.months || 7,
        start_date: params.startDate,
        end_date: params.endDate,
        provider_name: params.providerName
      }
    }),

  getTopServices: (params: {
    credentialId?: string;
    startDate?: string;
    endDate?: string;
    providerName?: string;
    page_size?: number;
    page?: number;
    sort_by?: string;
    sort_order?: string;
  }) => 
    apiClient.get('/api/v1/services/top', { 
      params: {
        credential_id: params.credentialId || 'test-credential-aws', // Use string credential_id
        start_date: params.startDate,
        end_date: params.endDate,
        provider_name: params.providerName,
        page_size: params.page_size || 10, // Backend expects page_size
        page: params.page || 1,
        sort_by: params.sort_by || 'cost',
        sort_order: params.sort_order || 'desc'
      }
    })
};
