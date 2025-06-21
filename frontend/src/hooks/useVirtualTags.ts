import { useState, useEffect, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import virtualTagsService from '@/api/virtualTags';
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

// Query keys
const QUERY_KEYS = {
  virtualTags: 'virtualTags',
  virtualTag: 'virtualTag',
  availableFields: 'availableFields',
  dashboardMetrics: 'dashboardMetrics',
  preview: 'preview'
} as const;

// Hook for virtual tags list
export const useVirtualTags = (params?: VirtualTagQueryParams) => {
  return useQuery({
    queryKey: [QUERY_KEYS.virtualTags, params],
    queryFn: () => virtualTagsService.getVirtualTags(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Hook for single virtual tag
export const useVirtualTag = (id: string) => {
  return useQuery({
    queryKey: [QUERY_KEYS.virtualTag, id],
    queryFn: () => virtualTagsService.getVirtualTag(id),
    enabled: !!id,
  });
};

// Hook for available fields
export const useAvailableFields = () => {
  return useQuery({
    queryKey: [QUERY_KEYS.availableFields],
    queryFn: virtualTagsService.getAvailableFields,
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
};

// Hook for dashboard metrics
export const useDashboardMetrics = (dateRange?: DateRangeFilter) => {
  return useQuery({
    queryKey: [QUERY_KEYS.dashboardMetrics, dateRange],
    queryFn: () => virtualTagsService.getDashboardMetrics(dateRange),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

// Hook for preview
export const useVirtualTagPreview = () => {
  const [preview, setPreview] = useState<AllocationPreview[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getPreview = async (id: string, dateRange: DateRangeFilter) => {
    setLoading(true);
    setError(null);
    try {
      const result = await virtualTagsService.getPreview(id, dateRange);
      setPreview(result);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao gerar preview';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const clearPreview = () => {
    setPreview(null);
    setError(null);
  };

  return {
    preview,
    loading,
    error,
    getPreview,
    clearPreview
  };
};

// Hook for CRUD operations
export const useVirtualTagMutations = () => {
  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: (data: CreateVirtualTagRequest) => virtualTagsService.createVirtualTag(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.virtualTags] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.dashboardMetrics] });
      toast.success('Virtual Tag criada com sucesso!');
    },
    onError: (error: any) => {
      const message = error?.response?.data?.message || 'Erro ao criar Virtual Tag';
      toast.error(message);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateVirtualTagRequest }) =>
      virtualTagsService.updateVirtualTag(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.virtualTags] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.virtualTag, id] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.dashboardMetrics] });
      toast.success('Virtual Tag atualizada com sucesso!');
    },
    onError: (error: any) => {
      const message = error?.response?.data?.message || 'Erro ao atualizar Virtual Tag';
      toast.error(message);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => virtualTagsService.deleteVirtualTag(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.virtualTags] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.dashboardMetrics] });
      toast.success('Virtual Tag excluída com sucesso!');
    },
    onError: (error: any) => {
      const message = error?.response?.data?.message || 'Erro ao excluir Virtual Tag';
      toast.error(message);
    },
  });

  const processAllocationMutation = useMutation({
    mutationFn: ({ dateRange, tagIds }: { dateRange: DateRangeFilter; tagIds?: string[] }) =>
      virtualTagsService.processAllocation(dateRange, tagIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.dashboardMetrics] });
      toast.success('Processamento de alocação iniciado!');
    },
    onError: (error: any) => {
      const message = error?.response?.data?.message || 'Erro ao processar alocação';
      toast.error(message);
    },
  });

  return {
    create: createMutation,
    update: updateMutation,
    delete: deleteMutation,
    processAllocation: processAllocationMutation,
  };
};

// Hook for form state management
export const useVirtualTagForm = (initialData?: VirtualTag) => {
  const [formData, setFormData] = useState({
    name: initialData?.name || '',
    description: initialData?.description || '',
    category: initialData?.category || 'project' as const,
    priority: initialData?.priority || 100,
    default_value: initialData?.default_value || '',
    is_active: initialData?.is_active ?? true,
    rules: initialData?.rules || [],
  });

  const [currentStep, setCurrentStep] = useState(0);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const updateField = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when field is updated
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateStep = (step: number): boolean => {
    const stepErrors: Record<string, string> = {};

    switch (step) {
      case 0: // Basic info
        if (!formData.name.trim()) {
          stepErrors.name = 'Nome é obrigatório';
        }
        if (formData.priority < 1 || formData.priority > 1000) {
          stepErrors.priority = 'Prioridade deve estar entre 1 e 1000';
        }
        break;
      case 1: // Rules
        if (formData.rules.length === 0) {
          stepErrors.rules = 'Pelo menos uma regra é obrigatória';
        }
        break;
    }

    setErrors(stepErrors);
    return Object.keys(stepErrors).length === 0;
  };

  const nextStep = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const prevStep = () => {
    setCurrentStep(prev => Math.max(0, prev - 1));
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      category: 'project',
      priority: 100,
      default_value: '',
      is_active: true,
      rules: [],
    });
    setCurrentStep(0);
    setErrors({});
  };

  return {
    formData,
    currentStep,
    errors,
    updateField,
    validateStep,
    nextStep,
    prevStep,
    resetForm,
    setFormData,
    setCurrentStep,
  };
};

// Hook for managing Virtual Tags data (legacy compatibility)
export const useVirtualTagsLegacy = () => {
  const [virtualTags, setVirtualTags] = useState<VirtualTagListResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState({
    page: 1,
    size: 10,
    total: 0
  });

  const fetchVirtualTags = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await virtualTagsService.getVirtualTags();
      setVirtualTags(response);
      
      setPagination({
        page: 1,
        size: response.length,
        total: response.length
      });

      console.log('✅ Virtual tags loaded:', response.length);
    } catch (err: any) {
      console.error('❌ Error fetching virtual tags:', err);
      
      if (err.response?.status === 401) {
        setError('Autenticação expirada - por favor, faça login novamente');
      } else if (err.response?.status === 403) {
        setError('Você não tem permissão para visualizar virtual tags');
      } else {
        setError(err.response?.data?.message || 'Erro ao carregar virtual tags');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const createTag = useCallback(async (tagData: CreateVirtualTagRequest) => {
    try {
      setLoading(true);
      setError(null);

      const response = await virtualTagsService.createVirtualTag(tagData);
      
      // Convert VirtualTag to VirtualTagListResponse format
      const listItem: VirtualTagListResponse = {
        id: response.id,
        name: response.name,
        category: response.category,
        is_active: response.is_active,
        priority: response.priority,
        rules_count: response.rules.length,
        created_at: response.created_at
      };
      
      // Add new tag to local state
      setVirtualTags(prev => [listItem, ...prev]);
      
      console.log('✅ Virtual tag created:', response.id);
      return response;
    } catch (err: any) {
      console.error('❌ Error creating virtual tag:', err);
      const errorMessage = err.response?.data?.message || 'Erro ao criar virtual tag';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  const updateTag = useCallback(async (tagId: string, tagData: Partial<UpdateVirtualTagRequest>) => {
    try {
      setLoading(true);
      setError(null);

      const response = await virtualTagsService.updateVirtualTag(tagId, tagData);
      
      // Convert VirtualTag to VirtualTagListResponse format
      const listItem: VirtualTagListResponse = {
        id: response.id,
        name: response.name,
        category: response.category,
        is_active: response.is_active,
        priority: response.priority,
        rules_count: response.rules.length,
        created_at: response.created_at
      };
      
      // Update tag in local state
      setVirtualTags(prev => prev.map(tag => tag.id === tagId ? listItem : tag));
      
      console.log('✅ Virtual tag updated:', tagId);
      return response;
    } catch (err: any) {
      console.error('❌ Error updating virtual tag:', err);
      const errorMessage = err.response?.data?.message || 'Erro ao atualizar virtual tag';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteTag = useCallback(async (tagId: string) => {
    try {
      setLoading(true);
      setError(null);

      await virtualTagsService.deleteVirtualTag(tagId);
      
      // Remove tag from local state
      setVirtualTags(prev => prev.filter(tag => tag.id !== tagId));
      
      console.log('✅ Virtual tag deleted:', tagId);
    } catch (err: any) {
      console.error('❌ Error deleting virtual tag:', err);
      const errorMessage = err.response?.data?.message || 'Erro ao excluir virtual tag';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  const duplicateTag = useCallback(async (tagId: string) => {
    try {
      setLoading(true);
      setError(null);

      // For now, we'll fetch the original tag and create a copy
      const originalTag = await virtualTagsService.getVirtualTag(tagId);
      const duplicateData: CreateVirtualTagRequest = {
        name: `${originalTag.name} (Cópia)`,
        description: originalTag.description,
        category: originalTag.category,
        priority: originalTag.priority + 1,
        default_value: originalTag.default_value,
        is_active: false,
        rules: originalTag.rules.map(rule => ({
          name: rule.name,
          description: rule.description,
          conditions: rule.conditions,
          action: rule.action,
          priority: rule.priority,
          logical_operator: rule.logical_operator,
          is_active: rule.is_active
        }))
      };
      
      const response = await virtualTagsService.createVirtualTag(duplicateData);
      
      // Convert VirtualTag to VirtualTagListResponse format
      const listItem: VirtualTagListResponse = {
        id: response.id,
        name: response.name,
        category: response.category,
        is_active: response.is_active,
        priority: response.priority,
        rules_count: response.rules.length,
        created_at: response.created_at
      };
      
      // Add duplicated tag to local state
      setVirtualTags(prev => [listItem, ...prev]);
      
      console.log('✅ Virtual tag duplicated:', response.id);
      return response;
    } catch (err: any) {
      console.error('❌ Error duplicating virtual tag:', err);
      const errorMessage = err.response?.data?.message || 'Erro ao duplicar virtual tag';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  const toggleActive = useCallback(async (tagId: string, isActive: boolean) => {
    try {
      const response = await virtualTagsService.updateVirtualTag(tagId, { is_active: isActive });
      
      // Convert VirtualTag to VirtualTagListResponse format
      const listItem: VirtualTagListResponse = {
        id: response.id,
        name: response.name,
        category: response.category,
        is_active: response.is_active,
        priority: response.priority,
        rules_count: response.rules.length,
        created_at: response.created_at
      };
      
      // Update tag in local state
      setVirtualTags(prev => prev.map(tag => tag.id === tagId ? listItem : tag));
      
      console.log(`✅ Virtual tag ${isActive ? 'activated' : 'deactivated'}:`, tagId);
      return response;
    } catch (err: any) {
      console.error('❌ Error toggling virtual tag:', err);
      const errorMessage = err.response?.data?.message || 'Erro ao alterar status da virtual tag';
      setError(errorMessage);
      throw new Error(errorMessage);
    }
  }, []);

  // Load tags on mount
  useEffect(() => {
    fetchVirtualTags();
  }, [fetchVirtualTags]);

  return {
    virtualTags,
    loading,
    error,
    pagination,
    fetchVirtualTags,
    createTag,
    updateTag,
    deleteTag,
    duplicateTag,
    toggleActive,
    refetch: fetchVirtualTags
  };
};

// Hook for virtual tag preview (simple version for compatibility)
export const useVirtualTagPreviewSimple = (tagId?: string) => {
  const [preview, setPreview] = useState<AllocationPreview | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generatePreview = useCallback(async (tagData: CreateVirtualTagRequest | VirtualTag) => {
    try {
      setLoading(true);
      setError(null);

      // Use the main service for preview
      let result;
      if (tagId) {
        result = await virtualTagsService.getPreview(tagId, {
          start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          end_date: new Date().toISOString().split('T')[0]
        });
      }
      
      setPreview(result?.[0] || null);
      console.log('✅ Preview generated');
      return result;
    } catch (err: any) {
      console.error('❌ Error generating preview:', err);
      const errorMessage = err.response?.data?.message || 'Erro ao gerar preview';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [tagId]);

  const validateRules = useCallback(async (rules: any[]) => {
    try {
      // Basic validation - in a real app this would call the backend
      return { isValid: true, errors: [] };
    } catch (err: any) {
      console.error('❌ Error validating rules:', err);
      throw new Error(err.response?.data?.message || 'Erro ao validar regras');
    }
  }, []);

  return {
    preview,
    loading,
    error,
    generatePreview,
    validateRules
  };
};