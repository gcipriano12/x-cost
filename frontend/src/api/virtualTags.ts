import { apiClient } from './client';
import {
  VirtualTag,
  VirtualTagListResponse,
  CreateVirtualTagRequest,
  UpdateVirtualTagRequest,
  AvailableField,
  AllocationPreview,
  DashboardMetrics,
  DateRangeFilter,
  VirtualTagQueryParams
} from '@/types/virtualTags';

const VIRTUAL_TAGS_BASE_URL = '/api/v1/virtual-tags';

export const virtualTagsService = {
  // CRUD operations
  async getVirtualTags(params?: VirtualTagQueryParams): Promise<VirtualTagListResponse[]> {
    const response = await apiClient.get(VIRTUAL_TAGS_BASE_URL, { params });
    return response.data;
  },

  async getVirtualTag(id: string): Promise<VirtualTag> {
    const response = await apiClient.get(`${VIRTUAL_TAGS_BASE_URL}/${id}`);
    return response.data;
  },

  async createVirtualTag(data: CreateVirtualTagRequest): Promise<VirtualTag> {
    const response = await apiClient.post(VIRTUAL_TAGS_BASE_URL, data);
    return response.data;
  },

  async updateVirtualTag(id: string, data: UpdateVirtualTagRequest): Promise<VirtualTag> {
    const response = await apiClient.put(`${VIRTUAL_TAGS_BASE_URL}/${id}`, data);
    return response.data;
  },

  async deleteVirtualTag(id: string): Promise<{ message: string }> {
    const response = await apiClient.delete(`${VIRTUAL_TAGS_BASE_URL}/${id}`);
    return response.data;
  },

  // Preview and processing
  async getPreview(id: string, dateRange: DateRangeFilter): Promise<AllocationPreview[]> {
    const response = await apiClient.post(`${VIRTUAL_TAGS_BASE_URL}/${id}/preview`, dateRange);
    return response.data;
  },

  async processAllocation(dateRange: DateRangeFilter, tagIds?: string[]): Promise<{ message: string }> {
    const response = await apiClient.post(`${VIRTUAL_TAGS_BASE_URL}/process-allocation`, {
      ...dateRange,
      tag_ids: tagIds
    });
    return response.data;
  },

  // Available fields and metadata
  async getAvailableFields(): Promise<AvailableField[]> {
    const response = await apiClient.get(`${VIRTUAL_TAGS_BASE_URL}/fields/available`);
    return response.data;
  },

  // Dashboard and metrics
  async getDashboardMetrics(dateRange?: DateRangeFilter): Promise<DashboardMetrics> {
    const response = await apiClient.get(`${VIRTUAL_TAGS_BASE_URL}/metrics/dashboard`, {
      params: dateRange
    });
    return response.data;
  }
};

export default virtualTagsService;
