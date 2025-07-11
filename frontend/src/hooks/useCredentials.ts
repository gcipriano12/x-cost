
import { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import { AWSCredentials, CredentialsResponse } from '../types/api';
import { useToast } from './use-toast';

export const useCredentials = () => {
  const [credentials, setCredentials] = useState<CredentialsResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const fetchCredentials = async (forceRefresh = false) => {
    setLoading(true);
    try {
      // Adicionar timestamp para evitar cache
      const url = forceRefresh 
        ? `/api/v1/credentials/?_t=${Date.now()}` 
        : '/api/v1/credentials/';
      
      const response = await apiClient.get<CredentialsResponse[]>(url);
      setCredentials(response.data);
    } catch (error: any) {
      toast({
        title: "Error fetching credentials",
        description: error.response?.data?.detail || "Failed to load credentials",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const createCredential = async (data: Omit<AWSCredentials, 'id'>) => {
    try {
      const response = await apiClient.post<CredentialsResponse>('/api/v1/credentials/', data);
      await fetchCredentials(true); // Forçar refresh
      toast({
        title: "Credential created",
        description: "AWS credential has been added successfully.",
      });
      return response.data;
    } catch (error: any) {
      toast({
        title: "Error creating credential",
        description: error.response?.data?.detail || "Failed to create credential",
        variant: "destructive",
      });
      throw error;
    }
  };

  const updateCredential = async (id: string, data: Partial<AWSCredentials>) => {
    try {
      const response = await apiClient.put<CredentialsResponse>(`/api/v1/credentials/${id}`, data);
      await fetchCredentials(true); // Forçar refresh
      toast({
        title: "Credential updated",
        description: "AWS credential has been updated successfully.",
      });
      return response.data;
    } catch (error: any) {
      toast({
        title: "Error updating credential",
        description: error.response?.data?.detail || "Failed to update credential",
        variant: "destructive",
      });
      throw error;
    }
  };

  const deleteCredential = async (id: string) => {
    try {
      await apiClient.delete(`/api/v1/credentials/${id}`);
      await fetchCredentials(true); // Forçar refresh
      toast({
        title: "Credential deleted",
        description: "AWS credential has been removed successfully.",
      });
    } catch (error: any) {
      toast({
        title: "Error deleting credential",
        description: error.response?.data?.detail || "Failed to delete credential",
        variant: "destructive",
      });
      throw error;
    }
  };

  const testCredential = async (id: string) => {
    try {
      setLoading(true);
      const response = await apiClient.post(`/api/v1/credentials/${id}/test`);
      toast({
        title: "Connection successful",
        description: "AWS credentials are valid and working.",
      });
      return response.data;
    } catch (error: any) {
      toast({
        title: "Connection failed",
        description: error.response?.data?.detail || "Failed to connect to AWS",
        variant: "destructive",
      });
      throw error;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCredentials(true); // Forçar refresh na primeira carga
  }, []);

  return {
    credentials,
    loading,
    fetchCredentials,
    createCredential,
    updateCredential,
    deleteCredential,
    testCredential,
  };
};
