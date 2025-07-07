
import { useState, useEffect, createContext, useContext } from 'react';
import { apiClient } from '../api/client';
import { LoginRequest, LoginResponse } from '../types/api';
import { useToast } from './use-toast';

interface User {
  username: string;
  // Dados básicos do usuário extraídos do token ou login
}

interface AuthContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  loading: boolean;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const useAuthProvider = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  const login = async (username: string, password: string) => {
    try {
      setLoading(true);
      const response = await apiClient.post<LoginResponse>('/api/v1/auth/login', {
        username,
        password,
      });
      
      localStorage.setItem('access_token', response.data.access_token);
      
      // Criar usuário básico a partir do login bem-sucedido
      setUser({ username });
      
      toast({
        title: "Login successful",
        description: "Welcome to X Cost!",
      });
    } catch (error: any) {
      console.error('Login error:', error.response?.data);
      toast({
        title: "Login failed",
        description: error.response?.data?.message || error.response?.data?.detail || "Invalid credentials",
        variant: "destructive",
      });
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      // Para JWT stateless, não precisamos chamar a API
      // Apenas removemos o token do localStorage
      localStorage.removeItem('access_token');
      setUser(null);
      
      toast({
        title: "Logout realizado",
        description: "Você foi desconectado com sucesso.",
      });
    } catch (error) {
      console.log('Error during logout:', error);
      // Mesmo se houver erro, garantimos o logout local
      localStorage.removeItem('access_token');
      setUser(null);
    }
  };

  useEffect(() => {
    const validateToken = async () => {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        setLoading(false);
        return;
      }

      // Verificação básica do formato do token
      if (token.length < 10) {
        localStorage.removeItem('access_token');
        setUser(null);
        setLoading(false);
        return;
      }

      // Como não temos endpoint /me, vamos assumir que o token é válido
      // se existe no localStorage. O interceptor da API vai lidar com tokens expirados
      setUser({ username: 'admin' });
      setLoading(false);
    };

    validateToken();
  }, []);

  return {
    user,
    login,
    logout,
    loading,
    isAuthenticated: !!user,
  };
};

export { AuthContext };
