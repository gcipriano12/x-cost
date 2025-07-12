import { apiClient } from '@/api/client';
import { KPIValue, KPICategoryResponse, KPIConfig, KPICategory } from '@/types/kpi.types';

class KPIService {
  private baseUrl = '/api/v1/kpis';

  /**
   * Obtém KPIs atuais
   */
  async getCurrentKPIs(category?: KPICategory): Promise<KPIValue[]> {
    const params = category ? { category } : undefined;
    const response = await apiClient.get(`${this.baseUrl}/current`, { params });
    return response.data.data.kpis;
  }

  /**
   * Obtém KPIs agrupados por categoria
   */
  async getKPIsByCategory(): Promise<KPICategoryResponse[]> {
    const response = await apiClient.get(`${this.baseUrl}/by-category`);
    return response.data.data.categories;
  }

  /**
   * Obtém histórico de um KPI
   */
  async getKPIHistory(kpiCode: string, days: number = 30) {
    const response = await apiClient.get(`${this.baseUrl}/history/${kpiCode}`, {
      params: { days }
    });
    return response.data.data;
  }

  /**
   * Atualiza configuração de KPI
   */
  async updateKPIConfig(kpiCode: string, config: Partial<KPIConfig>) {
    const response = await apiClient.put(`${this.baseUrl}/config/${kpiCode}`, config);
    return response.data.data;
  }

  /**
   * Força recálculo de KPIs (admin)
   */
  async calculateKPIs(date?: string) {
    const response = await apiClient.post(`${this.baseUrl}/calculate`, { 
      calculation_date: date 
    });
    return response.data;
  }
}

export default new KPIService();