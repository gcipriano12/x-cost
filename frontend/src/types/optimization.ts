// Cloud Optimization Types

export type SeverityLevel = 'low' | 'medium' | 'high' | 'critical';
export type EffortLevel = 'Baixo' | 'Médio' | 'Alto';
export type RiskLevel = 'low' | 'medium' | 'high';
export type HealthStatus = 'excellent' | 'good' | 'needs_attention' | 'critical';
export type CloudProvider = 'AWS' | 'Azure' | 'GCP' | 'Oracle';

export type AnomalyType = 'spike' | 'drift' | 'unusual_pattern' | 'cost_increase';
export type OpportunityType = 
  | 'rightsizing' 
  | 'reserved_instances' 
  | 'spot_instances'
  | 'storage_optimization' 
  | 'network_optimization'
  | 'idle_resources' 
  | 'scheduling';

// Cloud Anomaly Interface
export interface CloudAnomaly {
  id: string;
  provider: string;
  service: string;
  region?: string;
  anomaly_type: AnomalyType;
  severity: SeverityLevel;
  detected_at: string;
  cost_impact: number;
  currency: string;
  description: string;
  root_cause?: string;
  affected_resources: string[];
}

// Savings Opportunity Interface
export interface SavingsOpportunity {
  id: string;
  provider: string;
  service: string;
  region?: string;
  opportunity_type: OpportunityType;
  title: string;
  description: string;
  category: string;
  monthly_savings: number;
  annual_savings?: number;
  estimated_savings: number; // Legacy field for compatibility
  currency: string;
  confidence_level: string; // 'high', 'medium', 'low'
  confidence: number; // Numeric confidence level (0-100)
  implementation_effort: EffortLevel;
  implementation_effort_hours?: number;
  risk_level: RiskLevel;
  affected_resources: string[];
  resource_name?: string;
  action_required: string;
  detected_at: string;
  created_at: string;
}

// Optimization Recommendation Interface
export interface OptimizationRecommendation {
  id: string;
  provider: string;
  title: string;
  description: string;
  category: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  estimated_savings: number;
  implementation_effort: EffortLevel;
  risk_assessment: RiskLevel;
  action_items: string[];
  resources_affected: string[];
  timeline_estimate: string;
  roi_score: number;
  created_at: string;
}

// Optimization Summary Interface - updated to match API response
export interface OptimizationSummary {
  anomalies: {
    total_count: number;
    total_cost_impact: number;
    severity_breakdown: {
      high: number;
      medium: number;
      low: number;
      critical: number;
    };
    top_anomaly: {
      description: string;
      cost_impact: number;
      severity: string;
    };
  };
  savings_opportunities: {
    total_count: number;
    total_potential_savings: number;
    top_opportunity: {
      description: string;
      potential_savings: number;
      category: string;
    };
  };
  recommendations: {
    total_count: number;
    type_breakdown: Record<string, unknown>;
    high_priority_count: number;
  };
  optimization_metrics: {
    optimization_score: number;
    total_potential_impact: number;
    health_status: HealthStatus;
  };
  metadata: {
    provider: string | null;
    analysis_scope: string;
    last_updated: string;
    processing_time_seconds: number;
    requested_by: string;
  };
}

// API Response Types
export interface AnomaliesResponse {
  anomalies: CloudAnomaly[];
  total_count: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface SavingsOpportunitiesResponse {
  opportunities: SavingsOpportunity[];
  total_count: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface OptimizationRecommendationsResponse {
  recommendations: OptimizationRecommendation[];
  total_count: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// Filter and Query Types
export interface OptimizationFilters {
  provider?: string;
  days?: number;
  severity?: SeverityLevel;
  min_savings?: number;
  category?: string;
  page?: number;
  per_page?: number;
  force_refresh?: boolean;
}

export interface AnomaliesFilters extends OptimizationFilters {
  anomaly_type?: AnomalyType;
  service_name?: string;
  min_cost_impact?: number;
  max_cost_impact?: number;
  date_from?: string;
  date_to?: string;
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface SavingsFilters extends OptimizationFilters {
  max_savings?: number;
  confidence_level?: string;
  implementation_effort?: string;
  risk_level?: string;
  service_name?: string;
  search?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

// Statistics and Metrics Types
export interface OptimizationMetrics {
  score: number;
  health_status: HealthStatus;
  total_savings_potential: number;
  anomalies_resolved: number;
  opportunities_implemented: number;
  roi_achieved: number;
}

export interface TrendData {
  date: string;
  optimization_score: number;
  cost_savings: number;
  anomalies_count: number;
  opportunities_count: number;
}

export interface CategoryBreakdown {
  category: string;
  count: number;
  total_savings: number;
  percentage: number;
}

// Notification Types
export interface OptimizationNotification {
  id: string;
  type: 'anomaly' | 'opportunity' | 'recommendation' | 'score_change';
  severity: SeverityLevel;
  title: string;
  message: string;
  data: CloudAnomaly | SavingsOpportunity | OptimizationRecommendation;
  created_at: string;
  read: boolean;
  actions?: {
    label: string;
    action: string;
    primary?: boolean;
  }[];
}

// Plan and Implementation Types
export interface OptimizationPlan {
  id: string;
  name: string;
  description: string;
  opportunities: string[]; // IDs of selected opportunities
  estimated_total_savings: number;
  timeline_months: number;
  risk_assessment: RiskLevel;
  implementation_steps: {
    step: number;
    title: string;
    description: string;
    effort_estimate: number;
    dependencies: number[];
    completed: boolean;
  }[];
  created_at: string;
  updated_at: string;
  status: 'draft' | 'active' | 'completed' | 'paused';
}

// Configuration Types
export interface OptimizationSettings {
  alert_thresholds: {
    anomaly_cost_impact: number;
    opportunity_min_savings: number;
    score_change_threshold: number;
  };
  notification_preferences: {
    email_enabled: boolean;
    push_enabled: boolean;
    frequency: 'real_time' | 'daily' | 'weekly';
    severity_filter: SeverityLevel[];
  };
  auto_implementation: {
    enabled: boolean;
    low_risk_only: boolean;
    max_cost_impact: number;
    require_approval: boolean;
  };
  providers_priority: CloudProvider[];
  refresh_intervals: {
    anomalies: number; // minutes
    opportunities: number; // minutes
    summary: number; // minutes
  };
}