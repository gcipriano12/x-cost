# 🎨 Guia de Integração Frontend - X Cost API

Este guia fornece instruções completas para integrar a API FinOps com qualquer frontend, incluindo dicas específicas para o Lovable.

## 📋 Visão Geral da API

### **Base URL**: `http://localhost:8000` (desenvolvimento)

### **Principais Grupos de Endpoints**:
- **🔐 Autenticação**: `/api/v1/auth/*`
- **🗝️ Credenciais**: `/api/v1/credentials/*`
- **💰 Custos**: `/api/v1/costs/*`
- **📊 Analytics**: `/api/v1/analytics/*`
- **💳 Orçamentos**: `/api/v1/budgets/*`
- **📋 Auditoria**: `/api/v1/audit/*`
- **🏥 Sistema**: `/api/v1/health`, `/api/v1/system/*`

## 🔐 Sistema de Autenticação

### **1. Login do Usuário**

**Endpoint**: `POST /api/v1/auth/login`

```typescript
// Request
interface LoginRequest {
  username: string;
  password: string;
}

// Response
interface LoginResponse {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
  user: {
    id: string;
    username: string;
    email: string;
    role: "admin" | "finops_admin" | "operator" | "viewer";
    is_active: boolean;
    created_at: string;
    last_login?: string;
  };
}
```

**Exemplo de Implementação**:

```typescript
// auth.service.ts
export class AuthService {
  private baseUrl = 'http://localhost:8000';
  private tokenKey = 'finops_access_token';
  
  async login(username: string, password: string): Promise<LoginResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });
    
    if (!response.ok) {
      throw new Error('Login failed');
    }
    
    const data: LoginResponse = await response.json();
    
    // Salvar token
    localStorage.setItem(this.tokenKey, data.access_token);
    localStorage.setItem('finops_user', JSON.stringify(data.user));
    
    return data;
  }
  
  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }
  
  getUser(): User | null {
    const userStr = localStorage.getItem('finops_user');
    return userStr ? JSON.parse(userStr) : null;
  }
  
  logout(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem('finops_user');
  }
  
  isAuthenticated(): boolean {
    return !!this.getToken();
  }
  
  // Helper para requests autenticadas
  async authenticatedFetch(url: string, options: RequestInit = {}): Promise<Response> {
    const token = this.getToken();
    
    return fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
  }
}
```

### **2. Criar Usuário (Admin Only)**

**Endpoint**: `POST /api/v1/auth/users`

```typescript
interface CreateUserRequest {
  username: string;
  email: string;
  password: string;
  role: "admin" | "finops_admin" | "operator" | "viewer";
}

interface UserResponse {
  id: string;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

// auth.service.ts (continuação)
async createUser(userData: CreateUserRequest): Promise<UserResponse> {
  const response = await this.authenticatedFetch(
    `${this.baseUrl}/api/v1/auth/users`,
    {
      method: 'POST',
      body: JSON.stringify(userData),
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create user');
  }
  
  return response.json();
}
```

```typescript
// route-guard.tsx
import { useAuth } from './auth.context';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requiredRole 
}) => {
  const { user, isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  if (requiredRole && !requiredRole.includes(user?.role)) {
    return <div>Access Denied</div>;
  }
  
  return <>{children}</>;
};
```

## 🔍 Validações de Credenciais Avançadas

### **Validações por Provedor**

```typescript
// validation.service.ts
export class CredentialValidationService {
  
  // Validação AWS
  static validateAWSCredentials(credentials: AWSCredentials): string[] {
    const errors: string[] = [];
    
    if (!credentials.access_key_id.startsWith('AKIA')) {
      errors.push('AWS access key ID deve começar com AKIA');
    }
    
    if (credentials.secret_access_key.length < 20) {
      errors.push('AWS secret access key muito curto');
    }
    
    if (credentials.region && !/^[a-z]{2}-[a-z]+-\d$/.test(credentials.region)) {
      errors.push('Formato de região AWS inválido');
    }
    
    return errors;
  }
  
  // Validação Azure
  static validateAzureCredentials(credentials: AzureCredentials): string[] {
    const errors: string[] = [];
    
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
    
    if (!uuidRegex.test(credentials.subscription_id)) {
      errors.push('Subscription ID deve ser um UUID válido');
    }
    
    if (!uuidRegex.test(credentials.client_id)) {
      errors.push('Client ID deve ser um UUID válido');
    }
    
    if (!uuidRegex.test(credentials.tenant_id)) {
      errors.push('Tenant ID deve ser um UUID válido');
    }
    
    return errors;
  }
  
  // Validação GCP
  static validateGCPCredentials(credentials: any): string[] {
    const errors: string[] = [];
    
    if (!credentials.project_id || !/^[a-z][a-z0-9-]*[a-z0-9]$/.test(credentials.project_id)) {
      errors.push('Project ID do GCP deve seguir o padrão correto');
    }
    
    if (credentials.service_account_key) {
      try {
        const key = JSON.parse(credentials.service_account_key);
        if (!key.type || key.type !== 'service_account') {
          errors.push('Service account key inválida');
        }
      } catch {
        errors.push('Service account key deve ser um JSON válido');
      }
    }
    
    return errors;
  }
}
```

### **Hook de Validação React**

```typescript
// hooks/useCredentialValidation.ts
import { useState, useEffect } from 'react';

interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

export const useCredentialValidation = (
  providerType: string,
  credentials: any
): ValidationResult => {
  const [result, setResult] = useState<ValidationResult>({
    isValid: true,
    errors: [],
    warnings: []
  });
  
  useEffect(() => {
    let errors: string[] = [];
    let warnings: string[] = [];
    
    switch (providerType) {
      case 'AWS':
        errors = CredentialValidationService.validateAWSCredentials(credentials);
        break;
      case 'Azure':
        errors = CredentialValidationService.validateAzureCredentials(credentials);
        break;
      case 'GCP':
        errors = CredentialValidationService.validateGCPCredentials(credentials);
        break;
    }
    
    // Adicionar warnings para credenciais que expiram em breve
    if (credentials.expires_at) {
      const expiryDate = new Date(credentials.expires_at);
      const now = new Date();
      const daysUntilExpiry = Math.ceil((expiryDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
      
      if (daysUntilExpiry <= 30) {
        warnings.push(`Credencial expira em ${daysUntilExpiry} dias`);
      }
    }
    
    setResult({
      isValid: errors.length === 0,
      errors,
      warnings
    });
  }, [providerType, credentials]);
  
  return result;
};
```

### **1. Listar Credenciais**

**Endpoint**: `GET /api/v1/credentials`

```typescript
interface Credential {
  id: string;
  name: string;
  description?: string;
  provider_type: "AWS" | "Azure" | "GCP" | "Oracle Cloud";
  account_id?: string;
  status: "active" | "inactive" | "expired" | "validation_failed";
  last_validated?: string;
  validation_error?: string;
  expires_at?: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

// credentials.service.ts
export class CredentialsService {
  constructor(private auth: AuthService) {}
  
  async getCredentials(filters?: {
    provider_type?: string;
    status?: string;
    name_contains?: string;
    expires_before?: string;
    limit?: number;
    offset?: number;
  }): Promise<Credential[]> {
    const params = new URLSearchParams();
    if (filters?.provider_type) params.append('provider_type', filters.provider_type);
    if (filters?.status) params.append('status', filters.status);
    if (filters?.name_contains) params.append('name_contains', filters.name_contains);
    if (filters?.expires_before) params.append('expires_before', filters.expires_before);
    if (filters?.limit) params.append('limit', filters.limit.toString());
    if (filters?.offset) params.append('offset', filters.offset.toString());
    
    const response = await this.auth.authenticatedFetch(
      `${this.auth.baseUrl}/api/v1/credentials?${params}`
    );
    
    if (!response.ok) throw new Error('Failed to fetch credentials');
    return response.json();
  }
}
```

### **2. Criar Credencial**

**Endpoint**: `POST /api/v1/credentials`

```typescript
// Tipos específicos por provedor
interface AWSCredentials {
  access_key_id: string;
  secret_access_key: string;
  region?: string;
  account_id?: string;
  role_arn?: string;
  external_id?: string;
}

interface AzureCredentials {
  subscription_id: string;
  client_id: string;
  client_secret: string;
  tenant_id: string;
}

interface CreateCredentialRequest {
  name: string;
  description?: string;
  provider_type: "AWS" | "Azure" | "GCP" | "Oracle Cloud";
  credentials: AWSCredentials | AzureCredentials | any;
  expires_at?: string;
}

// Implementação
async createCredential(data: CreateCredentialRequest): Promise<Credential> {
  const response = await this.auth.authenticatedFetch(
    `${this.auth.baseUrl}/api/v1/credentials`,
    {
      method: 'POST',
      body: JSON.stringify(data),
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create credential');
  }
  
  return response.json();
}
```

### **3. Atualizar Credencial**

**Endpoint**: `PUT /api/v1/credentials/{id}`

```typescript
interface UpdateCredentialRequest {
  name?: string;
  description?: string;
  credentials?: AWSCredentials | AzureCredentials | any;
  status?: "active" | "inactive";
  expires_at?: string;
}

async updateCredential(id: string, data: UpdateCredentialRequest): Promise<Credential> {
  const response = await this.auth.authenticatedFetch(
    `${this.auth.baseUrl}/api/v1/credentials/${id}`,
    {
      method: 'PUT',
      body: JSON.stringify(data),
    }
  );
  
  if (!response.ok) throw new Error('Failed to update credential');
  return response.json();
}
```

### **4. Atualizar Status de Credencial**

**Endpoint**: `PATCH /api/v1/credentials/{id}/status`

```typescript
interface StatusUpdateRequest {
  status: "active" | "inactive";
}

async updateCredentialStatus(id: string, status: string): Promise<Credential> {
  const response = await this.auth.authenticatedFetch(
    `${this.auth.baseUrl}/api/v1/credentials/${id}/status`,
    {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    }
  );
  
  if (!response.ok) throw new Error('Failed to update status');
  return response.json();
}
```

### **5. Validar Credencial**

**Endpoint**: `POST /api/v1/credentials/{id}/validate`

```typescript
interface ValidationResult {
  is_valid: boolean;
  provider_type: string;
  account_info?: {
    account_id?: string;
    arn?: string;
    [key: string]: any;
  };
  permissions_check?: {
    cost_explorer?: boolean;
    s3_access?: boolean;
    [key: string]: boolean;
  };
  validation_timestamp: string;
  error_message?: string;
}

async validateCredential(id: string): Promise<ValidationResult> {
  const response = await this.auth.authenticatedFetch(
    `${this.auth.baseUrl}/api/v1/credentials/${id}/validate`,
    { method: 'POST' }
  );
  
  if (!response.ok) throw new Error('Validation failed');
  return response.json();
}
```

### **6. Testar Credenciais (Sem Salvar)**

**Endpoint**: `POST /api/v1/credentials/test`

```typescript
interface TestCredentialRequest {
  provider_type: "AWS" | "Azure" | "GCP";
  credentials: AWSCredentials | AzureCredentials | any;
}

async testCredentials(data: TestCredentialRequest): Promise<ValidationResult> {
  const response = await this.auth.authenticatedFetch(
    `${this.auth.baseUrl}/api/v1/credentials/test`,
    {
      method: 'POST',
      body: JSON.stringify(data),
    }
  );
  
  if (!response.ok) throw new Error('Test failed');
  return response.json();
}
```

### **7. Deletar Credencial**

**Endpoint**: `DELETE /api/v1/credentials/{id}`

```typescript
async deleteCredential(id: string, force: boolean = false): Promise<void> {
  const params = new URLSearchParams();
  if (force) params.append('force', 'true');
  
  const response = await this.auth.authenticatedFetch(
    `${this.auth.baseUrl}/api/v1/credentials/${id}?${params}`,
    { method: 'DELETE' }
  );
  
  if (!response.ok) throw new Error('Failed to delete credential');
}
```

## 📋 Sistema de Auditoria

### **1. Listar Logs de Auditoria**

**Endpoint**: `GET /api/v1/audit/logs`

```typescript
interface AuditLog {
  id: string;
  action: "create" | "update" | "delete" | "view" | "validate" | "rotate";
  username: string;
  timestamp: string;
  success: boolean;
  details?: {
    provider_type?: string;
    credential_name?: string;
    validation_result?: boolean;
    [key: string]: any;
  };
  ip_address?: string;
  user_agent?: string;
  error_message?: string;
}

interface AuditQueryParams {
  action?: string;
  username?: string;
  start_date?: string;
  end_date?: string;
  success?: boolean;
  limit?: number;
  offset?: number;
}

// audit.service.ts
export class AuditService {
  constructor(private auth: AuthService) {}
  
  async getAuditLogs(filters?: AuditQueryParams): Promise<AuditLog[]> {
    const params = new URLSearchParams();
    if (filters?.action) params.append('action', filters.action);
    if (filters?.username) params.append('username', filters.username);
    if (filters?.start_date) params.append('start_date', filters.start_date);
    if (filters?.end_date) params.append('end_date', filters.end_date);
    if (filters?.success !== undefined) params.append('success', filters.success.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    if (filters?.offset) params.append('offset', filters.offset.toString());
    
    const response = await this.auth.authenticatedFetch(
      `${this.auth.baseUrl}/api/v1/audit/logs?${params}`
    );
    
    if (!response.ok) throw new Error('Failed to fetch audit logs');
    return response.json();
  }
}
```

## 💰 Dados de Custos

### **1. Obter Dados de Custo**

**Endpoint**: `GET /api/v1/costs`

```typescript
interface CostData {
  id: number;
  provider_name: string;
  service_name: string;
  billing_period_start: string;
  billing_period_end: string;
  effective_cost: number;
  billing_currency: string;
  resource_id?: string;
  resource_type?: string;
  region?: string;
  tags?: Record<string, any>;
  created_at: string;
}

interface CostQueryParams {
  provider_name?: string;
  service_name?: string;
  resource_type?: string;
  start_date?: string;
  end_date?: string;
  limit?: number;
  offset?: number;
}

export class CostService {
  constructor(private auth: AuthService) {}
  
  async getCosts(params?: CostQueryParams): Promise<CostData[]> {
    const searchParams = new URLSearchParams();
    
    Object.entries(params || {}).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.append(key, String(value));
      }
    });
    
    const response = await this.auth.authenticatedFetch(
      `${this.auth.baseUrl}/api/v1/costs?${searchParams}`
    );
    
    return response.json();
  }
}
```

### **2. Resumo de Custos**

**Endpoint**: `GET /api/v1/costs/summary`

```typescript
interface CostSummary {
  provider_name: string;
  service_name: string;
  period_start: string;
  period_end: string;
  total_cost: number;
  record_count: number;
}

async getCostSummary(groupBy: 'service' | 'provider' | 'region' = 'service'): Promise<CostSummary[]> {
  const response = await this.auth.authenticatedFetch(
    `${this.auth.baseUrl}/api/v1/costs/summary?group_by=${groupBy}`
  );
  
  return response.json();
}
```

## 📊 Analytics e Relatórios

### **1. Tendência de Custos**

**Endpoint**: `GET /api/v1/analytics/trend`

```typescript
interface TrendData {
  period: string;
  total_cost: number;
  record_count: number;
  trend_percentage?: number;
  cost_change: number;
}

async getCostTrend(params: {
  provider_name?: string;
  service_name?: string;
  start_date?: string;
  end_date?: string;
  period?: 'daily' | 'weekly' | 'monthly';
}): Promise<{trend_data: TrendData[]}> {
  const searchParams = new URLSearchParams();
  
  Object.entries(params).forEach(([key, value]) => {
    if (value) searchParams.append(key, value);
  });
  
  const response = await this.auth.authenticatedFetch(
    `${this.auth.baseUrl}/api/v1/analytics/trend?${searchParams}`
  );
  
  return response.json();
}
```

### **2. Previsão de Custos**

**Endpoint**: `GET /api/v1/analytics/forecast`

```typescript
interface ForecastData {
  forecast_period_days: number;
  total_forecasted_cost: number;
  average_daily_forecast: number;
  model_accuracy: {
    r_squared: number;
    mean_absolute_error: number;
  };
  daily_forecasts: Array<{
    date: string;
    forecasted_cost: number;
    confidence_lower: number;
    confidence_upper: number;
  }>;
}

async getForecast(params: {
  provider_name?: string;
  service_name?: string;
  forecast_days?: number;
}): Promise<ForecastData> {
  const searchParams = new URLSearchParams();
  
  Object.entries(params).forEach(([key, value]) => {
    if (value) searchParams.append(key, String(value));
  });
  
  const response = await this.auth.authenticatedFetch(
    `${this.auth.baseUrl}/api/v1/analytics/forecast?${searchParams}`
  );
  
  return response.json();
}
```

## 🎨 Componentes React Exemplo

### **1. Componente de Login**

```typescript
// LoginForm.tsx
import React, { useState } from 'react';
import { useAuth } from './auth.context';

export const LoginForm: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { login } = useAuth();
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      await login(username, password);
      // Redirect será feito pelo AuthContext
    } catch (err) {
      setError('Login failed. Check your credentials.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="login-form">
      <div className="form-group">
        <label htmlFor="username">Username</label>
        <input
          id="username"
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>
      
      {error && <div className="error">{error}</div>}
      
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
};
```

### **2. Lista de Credenciais**

```typescript
// CredentialsList.tsx
import React, { useState, useEffect } from 'react';
import { CredentialsService } from './credentials.service';

interface CredentialsListProps {
  onEdit: (credential: Credential) => void;
  onDelete: (id: string) => void;
}

export const CredentialsList: React.FC<CredentialsListProps> = ({ onEdit, onDelete }) => {
  const [credentials, setCredentials] = useState<Credential[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({
    provider_type: '',
    status: '',
  });
  
  const credentialsService = new CredentialsService(/* auth service */);
  
  useEffect(() => {
    loadCredentials();
  }, [filter]);
  
  const loadCredentials = async () => {
    try {
      const data = await credentialsService.getCredentials(filter);
      setCredentials(data);
    } catch (error) {
      console.error('Failed to load credentials:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleValidate = async (id: string) => {
    try {
      const result = await credentialsService.validateCredential(id);
      alert(`Validation ${result.is_valid ? 'successful' : 'failed'}`);
      loadCredentials(); // Refresh list
    } catch (error) {
      alert('Validation failed');
    }
  };
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div className="credentials-list">
      {/* Filters */}
      <div className="filters">
        <select 
          value={filter.provider_type}
          onChange={(e) => setFilter({...filter, provider_type: e.target.value})}
        >
          <option value="">All Providers</option>
          <option value="AWS">AWS</option>
          <option value="Azure">Azure</option>
          <option value="GCP">GCP</option>
          <option value="Oracle Cloud">Oracle Cloud</option>
        </select>
        
        <select
          value={filter.status}
          onChange={(e) => setFilter({...filter, status: e.target.value})}
        >
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="validation_failed">Failed</option>
        </select>
      </div>
      
      {/* Table */}
      <table className="credentials-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Provider</th>
            <th>Status</th>
            <th>Last Validated</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {credentials.map((credential) => (
            <tr key={credential.id}>
              <td>{credential.name}</td>
              <td>{credential.provider_type}</td>
              <td>
                <span className={`status status-${credential.status}`}>
                  {credential.status}
                </span>
              </td>
              <td>
                {credential.last_validated 
                  ? new Date(credential.last_validated).toLocaleDateString()
                  : 'Never'
                }
              </td>
              <td>
                <button onClick={() => handleValidate(credential.id)}>
                  Validate
                </button>
                <button onClick={() => onEdit(credential)}>
                  Edit
                </button>
                <button onClick={() => onDelete(credential.id)}>
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
```

### **3. Dashboard de Custos**

```typescript
// CostDashboard.tsx
import React, { useState, useEffect } from 'react';
import { Line, Bar, Pie } from 'react-chartjs-2';

export const CostDashboard: React.FC = () => {
  const [trendData, setTrendData] = useState<any>(null);
  const [summaryData, setSummaryData] = useState<any>(null);
  const [forecastData, setForecastData] = useState<any>(null);
  
  useEffect(() => {
    loadDashboardData();
  }, []);
  
  const loadDashboardData = async () => {
    // Implementar chamadas para múltiplos endpoints
    // Usar Promise.all para carregamento paralelo
  };
  
  return (
    <div className="cost-dashboard">
      <div className="dashboard-grid">
        {/* KPIs */}
        <div className="kpi-section">
          <div className="kpi-card">
            <h3>Total Cost (This Month)</h3>
            <div className="kpi-value">$12,345</div>
          </div>
          <div className="kpi-card">
            <h3>Cost Trend</h3>
            <div className="kpi-value trend-up">+5.2%</div>
          </div>
        </div>
        
        {/* Charts */}
        <div className="chart-section">
          <div className="chart-container">
            <h3>Cost Trend</h3>
            {trendData && <Line data={trendData} />}
          </div>
          
          <div className="chart-container">
            <h3>Cost by Provider</h3>
            {summaryData && <Pie data={summaryData} />}
          </div>
        </div>
      </div>
    </div>
  );
};
```

## 🤖 Integração com Lovable

### **Prompt para o Lovable - Configuração Inicial**

```
Preciso integrar minha aplicação React com uma API FinOps. Aqui estão as especificações:

**API Base URL**: http://localhost:8000

**Sistema de Autenticação**:
- Endpoint de login: POST /api/v1/auth/login
- Body: {"username": string, "password": string}
- Response: {"access_token": string, "token_type": "bearer", "user": {...}}
- Todas as demais requisições precisam do header: Authorization: Bearer {token}

**Principais Endpoints**:
1. GET /api/v1/credentials - Lista credenciais de cloud
2. POST /api/v1/credentials - Cria nova credencial
3. GET /api/v1/costs - Obtém dados de custo
4. GET /api/v1/analytics/trend - Tendência de custos
5. GET /api/v1/analytics/forecast - Previsão de custos

**Tipos TypeScript que preciso**:
```typescript
interface User {
  id: string;
  username: string;
  role: "admin" | "finops_admin" | "operator" | "viewer";
}

interface Credential {
  id: string;
  name: string;
  provider_type: "AWS" | "Azure" | "GCP" | "Oracle Cloud";
  status: "active" | "inactive" | "validation_failed";
  created_at: string;
}

interface CostData {
  provider_name: string;
  service_name: string;
  effective_cost: number;
  billing_period_start: string;
}
```

Por favor, crie:
1. Um serviço de autenticação com login/logout
2. Um contexto React para gerenciar estado de auth
3. Serviços para consumir a API de credenciais e custos
4. Componentes protegidos por autenticação
5. Um dashboard básico mostrando credenciais e custos
```

### **Prompt para o Lovable - Componentes Específicos**

```
Agora preciso de componentes específicos para o FinOps:

**1. Formulário de Credenciais AWS**:
- Campos: name, access_key_id, secret_access_key, region, account_id
- Validação: access_key deve começar com AKIA, secret_access_key min 40 chars
- Endpoint: POST /api/v1/credentials
- Body exemplo:
```json
{
  "name": "aws-prod",
  "provider_type": "AWS",
  "credentials": {
    "access_key_id": "AKIA...",
    "secret_access_key": "...",
    "region": "us-east-1"
  }
}
```

**2. Dashboard de Custos**:
- Chart de linha para tendência (endpoint: GET /api/v1/analytics/trend)
- Chart de pizza para custos por provedor (GET /api/v1/costs/summary)
- Cards com KPIs: custo total, tendência, próxima previsão
- Filtros por: provider, período (último mês, trimestre)

**3. Lista de Credenciais**:
- Tabela com: nome, provedor, status, última validação
- Ações: validar, editar, excluir
- Status com cores: green (active), red (validation_failed), gray (inactive)
- Botão para validar: POST /api/v1/credentials/{id}/validate

Use Tailwind CSS e bibliotecas como Chart.js ou Recharts para os gráficos.
```

### **Prompt para o Lovable - Features Avançadas**

```
Adicione estas funcionalidades avançadas ao FinOps:

**1. Sistema de Roles e Permissões**:
- admin: pode tudo
- finops_admin: pode gerenciar credenciais
- operator: pode ver e validar credenciais
- viewer: apenas visualização

Baseado no user.role, esconda/mostre botões e páginas.

**2. Notificações e Alertas**:
- Credenciais expirando em 30 dias
- Validações que falharam
- Custos acima do orçamento
- Endpoint: GET /api/v1/budgets/alerts

**3. Filtros e Busca Avançada**:
- Busca por nome de credencial
- Filtros por múltiplos provedores
- Filtros por período de data
- Filtros por range de custo
- Ordenação por custo, data, nome

**4. Export de Dados**:
- Botão para exportar dados de custo como CSV
- Relatório PDF com gráficos
- Endpoint: GET /api/v1/costs?format=csv

**5. Histórico e Auditoria**:
- Timeline de ações do usuário
- Logs de validação de credenciais
- Histórico de alterações
- Endpoint: GET /api/v1/audit/logs

Mantenha a interface limpa e responsiva. Use loading states e error handling adequados.
```

### **Prompt para o Lovable - Tratamento de Erros**

```
Implemente tratamento robusto de erros para a API FinOps:

**Códigos de Status Esperados**:
- 200: Sucesso
- 201: Criado com sucesso
- 400: Dados inválidos (mostrar mensagem específica)
- 401: Não autenticado (redirecionar para login)
- 403: Sem permissão (mostrar "Acesso negado")
- 404: Recurso não encontrado
- 409: Conflito (ex: credencial já existe)
- 422: Validação falhou (mostrar erros de campo)
- 500: Erro interno (mostrar "Tente novamente")

**Padrão de Response de Erro**:
```json
{
  "detail": "Mensagem de erro",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-06-03T10:00:00Z"
}
```

**Implementar**:
1. Interceptor HTTP para tratar erros globalmente
2. Toast notifications para sucesso/erro
3. Loading states em todas as operações
4. Retry automático para erros 5xx
5. Offline detection e mensagem apropriada
6. Validação client-side antes de enviar para API

**Mensagens de Erro Específicas**:
- "Credencial já existe com este nome"
- "Formato inválido da chave AWS"
- "Sessão expirada, faça login novamente"
- "Você não tem permissão para esta ação"
```

## 📱 Estados da Aplicação

### **1. Estado de Autenticação**

```typescript
// auth.context.tsx
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface AuthContextType extends AuthState {
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => void;
}
```

### **2. Estado de Credenciais**

```typescript
// credentials.context.tsx
interface CredentialsState {
  credentials: Credential[];
  loading: boolean;
  error: string | null;
  filters: {
    provider_type: string;
    status: string;
    search: string;
  };
}
```

### **3. Estado de Custos**

```typescript
// costs.context.tsx
interface CostsState {
  costs: CostData[];
  summary: CostSummary[];
  trend: TrendData[];
  forecast: ForecastData | null;
  loading: {
    costs: boolean;
    summary: boolean;
    trend: boolean;
    forecast: boolean;
  };
  dateRange: {
    start: string;
    end: string;
  };
}
```

## 🎯 Componentes UI Essenciais

### **1. Loading States**

```typescript
// LoadingSpinner.tsx
export const LoadingSpinner: React.FC<{ size?: 'sm' | 'md' | 'lg' }> = ({ size = 'md' }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8', 
    lg: 'w-12 h-12'
  };
  
  return (
    <div className={`animate-spin rounded-full border-2 border-gray-300 border-t-blue-600 ${sizeClasses[size]}`} />
  );
};

// LoadingButton.tsx
export const LoadingButton: React.FC<{
  loading: boolean;
  children: React.ReactNode;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
}> = ({ loading, children, onClick, variant = 'primary' }) => {
  return (
    <button
      onClick={onClick}
      disabled={loading}
      className={`px-4 py-2 rounded-md ${variant === 'primary' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
    >
      {loading ? <LoadingSpinner size="sm" /> : children}
    </button>
  );
};
```

### **2. Status Badges**

```typescript
// StatusBadge.tsx
export const StatusBadge: React.FC<{ 
  status: 'active' | 'inactive' | 'validation_failed' | 'expired' 
}> = ({ status }) => {
  const statusConfig = {
    active: { color: 'bg-green-100 text-green-800', text: 'Active' },
    inactive: { color: 'bg-gray-100 text-gray-800', text: 'Inactive' },
    validation_failed: { color: 'bg-red-100 text-red-800', text: 'Failed' },
    expired: { color: 'bg-yellow-100 text-yellow-800', text: 'Expired' }
  };
  
  const config = statusConfig[status];
  
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
      {config.text}
    </span>
  );
};
```

### **3. Error Boundary**

```typescript
// ErrorBoundary.tsx
export class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }
  
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }
  
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <details>
            {this.state.error?.message}
          </details>
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      );
    }
    
    return this.props.children;
  }
}
```

## 🔧 Hooks Customizados

### **1. Hook para API calls**

```typescript
// useApi.ts
export function useApi<T>(
  apiCall: () => Promise<T>,
  dependencies: any[] = []
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const execute = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiCall();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, dependencies);
  
  useEffect(() => {
    execute();
  }, [execute]);
  
  return { data, loading, error, refetch: execute };
}
```

### **2. Hook para debounced search**

```typescript
// useDebounce.ts
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);
  
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);
    
    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);
  
  return debouncedValue;
}
```

## 📊 Configurações de Gráficos

### **1. Chart.js Configuration**

```typescript
// chartConfig.ts
export const lineChartConfig = {
  responsive: true,
  plugins: {
    legend: {
      position: 'top' as const,
    },
    title: {
      display: true,
      text: 'Cost Trend Over Time',
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        callback: function(value: any) {
          return ' + value.toLocaleString();
        }
      }
    }
  }
};

export const pieChartConfig = {
  responsive: true,
  plugins: {
    legend: {
      position: 'right' as const,
    },
    tooltip: {
      callbacks: {
        label: function(context: any) {
          return context.label + ':  + context.parsed.toLocaleString();
        }
      }
    }
  }
};
```

## 🎨 Estilos CSS Customizados

### **1. Tema de Cores**

```css
/* styles/theme.css */
:root {
  --primary-blue: #2563eb;
  --primary-blue-dark: #1d4ed8;
  --success-green: #10b981;
  --warning-yellow: #f59e0b;
  --error-red: #ef4444;
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-500: #6b7280;
  --gray-900: #111827;
}

.btn-primary {
  @apply bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors;
}

.card {
  @apply bg-white rounded-lg shadow-md p-6 border border-gray-200;
}

.table-row {
  @apply border-b border-gray-200 hover:bg-gray-50 transition-colors;
}

.status-active {
  @apply bg-green-100 text-green-800;
}

.status-inactive {
  @apply bg-gray-100 text-gray-800;
}

.status-failed {
  @apply bg-red-100 text-red-800;
}
```

## 🔄 Fluxo de Desenvolvimento

### **1. Setup Inicial**

1. **Configurar Autenticação**
2. **Criar Serviços da API**
3. **Implementar Contextos**
4. **Criar Componentes Base**
5. **Adicionar Roteamento Protegido**

### **2. Features por Prioridade**

1. **Login/Logout** (Essencial)
2. **Lista de Credenciais** (Core)
3. **Criar/Editar Credenciais** (Core)
4. **Dashboard de Custos** (Importante)
5. **Relatórios e Analytics** (Enhancement)
6. **Auditoria e Logs** (Nice to have)

### **3. Checklist de Qualidade**

- [ ] Tratamento de erros em todos os endpoints
- [ ] Loading states em todas as operações
- [ ] Validação de formulários
- [ ] Responsividade mobile
- [ ] Acessibilidade básica
- [ ] Testes unitários dos componentes principais
- [ ] Documentação dos componentes

---

## ✅ Resumo para Integração com Lovable

### **🎯 O que pedir ao Lovable:**

1. **"Crie um serviço de autenticação JWT que faça login na API FinOps e gerencie tokens"**

2. **"Implemente um dashboard com gráficos de custo usando a API /analytics/trend"**

3. **"Crie um CRUD completo para credenciais cloud com validação em tempo real"**

4. **"Adicione sistema de roles (admin/viewer) com proteção de rotas"**

5. **"Implemente tratamento de erros HTTP com notificações toast"**

### **🔧 Configurações que o Lovable precisa saber:**

- **API Base**: `http://localhost:8000`
- **Autenticação**: JWT Bearer Token
- **Principais endpoints**: `/auth/login`, `/credentials`, `/costs`, `/analytics`
- **Tipos TypeScript**: Usar as interfaces fornecidas acima
- **UI Framework**: Tailwind CSS + componentes customizados
- **Charts**: Chart.js ou Recharts para visualizações

**🚀 Com estas especificações, o Lovable conseguirá criar uma integração completa e funcional com sua API FinOps!**