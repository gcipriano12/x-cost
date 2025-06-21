// Virtual Tags Type Definitions for X-Cost
// Based on FinOut specification and X-Cost requirements

export type VirtualTagCategory = 
  | 'business_unit' 
  | 'project' 
  | 'environment' 
  | 'cost_center' 
  | 'department' 
  | 'team' 
  | 'application' 
  | 'owner' 
  | 'custom';

export type RuleOperator = 
  | 'equals' 
  | 'not_equals' 
  | 'contains' 
  | 'not_contains' 
  | 'starts_with' 
  | 'ends_with' 
  | 'regex' 
  | 'in' 
  | 'not_in' 
  | 'greater_than' 
  | 'less_than' 
  | 'greater_equal' 
  | 'less_equal';

export type LogicalOperator = 'AND' | 'OR';

export type RuleActionType = 'set_value' | 'extract_from_field' | 'map_value' | 'calculate' | 'default';

export interface RuleCondition {
  field: string;
  operator: RuleOperator;
  value: string | number | string[];
  case_sensitive?: boolean;
}

export interface RuleAction {
  type: RuleActionType;
  value?: string;
  field?: string;
  mapping?: Record<string, string>;
  pattern?: string;
  default_value?: string;
}

export interface VirtualTagRule {
  id?: string;
  name: string;
  description?: string;
  conditions: RuleCondition[];
  action: RuleAction;
  priority: number;
  logical_operator: LogicalOperator;
  is_active?: boolean;
  created_at?: string;
}

export interface VirtualTag {
  id: string;
  name: string;
  description?: string;
  category: VirtualTagCategory;
  is_active: boolean;
  priority: number;
  default_value?: string;
  created_at: string;
  updated_at: string;
  created_by: string;
  rules: VirtualTagRule[];
}

// API Request/Response interfaces
export interface CreateVirtualTagRequest {
  name: string;
  description?: string;
  category: VirtualTagCategory;
  is_active?: boolean;
  priority: number;
  default_value?: string;
  rules: Omit<VirtualTagRule, 'id' | 'created_at'>[];
}

export interface UpdateVirtualTagRequest extends Partial<CreateVirtualTagRequest> {
  rules?: Omit<VirtualTagRule, 'id' | 'created_at'>[];
}

export interface VirtualTagListResponse {
  id: string;
  name: string;
  category: VirtualTagCategory;
  is_active: boolean;
  priority: number;
  rules_count: number;
  created_at: string;
}

// Available fields for rule building
export interface AvailableField {
  field_name: string;
  field_label: string;
  field_type: 'string' | 'number' | 'boolean' | 'date' | 'json';
  description?: string;
  sample_values?: string[];
}

// Preview and metrics interfaces
export interface AllocationPreview {
  cost_record_id: number;
  provider_name: string;
  service_name: string;
  resource_id?: string;
  cost_amount: number;
  tag_value?: string;
  rule_applied?: string;
  service?: string;
  billing_period_start: string;
}

export interface DateRangeFilter {
  start_date: string;
  end_date: string;
}

export interface CoverageMetrics {
  total_cost: string;
  allocated_cost: string;
  unallocated_cost: string;
  allocation_percentage: number;
  total_records: number;
  allocated_records: number;
  virtual_tags_count: number;
  rules_count: number;
}

export interface AllocationBreakdown {
  virtual_tag_name: string;
  category: VirtualTagCategory;
  total_cost: string;
  record_count: number;
  percentage_of_total: number;
  top_values: Array<{ value: string; cost: string; count: number }>;
}

export interface UnallocatedCost {
  provider_name: string;
  service_name: string;
  resource_type?: string;
  cost_amount: string;
  record_count: number;
  percentage_of_unallocated: number;
}

export interface RuleConflict {
  virtual_tag1_id: string;
  virtual_tag1_name: string;
  virtual_tag2_id: string;
  virtual_tag2_name: string;
  conflict_type: string;
  description: string;
  sample_records: number;
}

export interface DashboardMetrics {
  coverage_metrics: CoverageMetrics;
  allocation_breakdown: AllocationBreakdown[];
  recent_processing: Array<{
    processing_id: string;
    status: string;
    start_date: string;
    end_date: string;
    records_processed: number;
    records_allocated: number;
    total_cost_allocated: number;
    processing_time_seconds?: number;
    created_at: string;
    error_message?: string;
  }>;
  rule_conflicts: RuleConflict[];
  unallocated_summary: {
    total_unallocated: string;
    top_unallocated_services: UnallocatedCost[];
    unallocated_percentage: number;
  };
}

// Form interfaces
export interface VirtualTagFormData {
  name: string;
  description: string;
  category: VirtualTagCategory;
  priority: number;
  default_value: string;
  is_active: boolean;
  rules: VirtualTagRule[];
}

// Query parameters
export interface VirtualTagQueryParams {
  category?: VirtualTagCategory;
  is_active?: boolean;
  search?: string;
  skip?: number;
  limit?: number;
}

export interface DashboardMetrics {
  totalCoveragePercentage: number;
  categoryBreakdown: CategoryBreakdown[];
  topUnallocatedServices: UnallocatedService[];
  conflictCount: number;
  lastProcessedAt: string;
}

export interface CategoryBreakdown {
  category: VirtualTagCategory;
  count: number;
  allocatedCost: number;
  percentage: number;
}

export interface UnallocatedService {
  service: string;
  provider: string;
  cost: number;
  resourceCount: number;
}

// Form step interfaces for multi-step form
export interface VirtualTagFormData {
  // Step 1: Basic info
  name: string;
  description: string;
  category: VirtualTagCategory;
  isActive: boolean;
  priority: number;
  defaultValue: string;
  
  // Step 2: Rules
  rules: VirtualTagRule[];
  
  // Step 3: Preview (read-only)
  preview?: AllocationPreview;
}

// Validation schemas
export interface ValidationError {
  field: string;
  message: string;
  code: string;
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
}

// Filter and sort options for list view
export interface VirtualTagFilters {
  search?: string;
  category?: VirtualTagCategory;
  isActive?: boolean;
  createdBy?: string;
  dateRange?: {
    start: string;
    end: string;
  };
}

export interface VirtualTagSortOptions {
  field: 'name' | 'category' | 'priority' | 'createdAt' | 'updatedAt';
  direction: 'asc' | 'desc';
}

export interface VirtualTagListParams {
  page?: number;
  size?: number;
  filters?: VirtualTagFilters;
  sort?: VirtualTagSortOptions;
}

// Chart data interfaces for dashboard
export interface AllocationChartData {
  category: VirtualTagCategory;
  allocated: number;
  unallocated: number;
  total: number;
}

export interface TrendChartData {
  date: string;
  allocatedCost: number;
  unallocatedCost: number;
  coveragePercentage: number;
}